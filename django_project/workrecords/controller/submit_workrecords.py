from django.http import JsonResponse
from workrecords.config import constant
from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from workrecords.services import work_record_service
from workrecords.utils import encryption_utils

import json
from mydata import mysql_base
import pandas as pd
import hashlib
import os
import shutil 

def work_record(request):
    """
    如果请求为get 则进行查询工单详细内容
    如果为post, 就进行添加工单
    """
    # 判断请求类型
    if request.method == 'GET':
        # 获得GET请求后面的参数信息
        search_filter = request.GET.get('searchFilter')
        search_filter = json.loads(search_filter)

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if search_filter["beginData"] <= "2023-12-31" and search_filter["endData"] >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为两个模板，请求时间不得跨越2023与2024年。"})
        
        curr_page = int(request.GET.get('page', default='1'))
        curr_page_size = int(request.GET.get('pageSize', default='10'))

        try:
            detail = work_record_service.get_work_record_detail(search_filter, curr_page, curr_page_size)
            amount = work_record_service.get_work_record_count(search_filter)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': detail, 'amount': amount}, json_dumps_params={'ensure_ascii': False})

    elif request.method == 'POST':
        work_record_detail_form = json.loads(request.body)
        fid = encryption_utils.md5_encryption(str(work_record_detail_form.get("registerDate"))+"-"+str(work_record_detail_form.get("agencyName")))
        try:
            work_record_service.add_work_record(fid, work_record_detail_form)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={ 'message': "插入成功!"}, json_dumps_params={'ensure_ascii': False})

def work_record_group_add(request):
    if request.method == 'POST':
        error_msg=[]

        # 进行暂存上传文件的目录的创建
        try:
            dir_path = os.path.join(constant.MEDIA_ROOT, "111")
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        except:
            return JsonResponse({'status': 500, 'data': "", 'message': "服务端创建缓存文件夹失败。"}, json_dumps_params={'ensure_ascii': False})

        files = request.FILES.values()
        for i in range(len(files)):
            file = files[i]
            print(f"receive file {file}")

            try:
                filename = os.path.join(dir_path, file.name)
                # 将文件存入服务器
                with open(filename, 'wb+') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                    f.close()
            except Exception as e: 
                print(e)
                print(f"服务端缓存文件{file.name}失败。")
                error_msg.append(f"服务端缓存文件{file.name}失败， 请重新尝试。")
                continue

            try:
                # 根据文件类型进行读取
                file_extension = filename.split('.')[-1]
                if file_extension == 'xlsx' or file_extension == 'xls': 
                    dataframe = pd.read_excel(io=filename, parse_dates=["登记日期"])
                    dataframe['登记日期'] = dataframe['登记日期'].apply(lambda x: str(pd.to_datetime(x).date()))
                    dataframe['解决日期'] = dataframe['解决日期'].apply(lambda x: str(pd.to_datetime(x).date()))
                elif file_extension == 'csv':
                    dataframe = pd.read_csv(io=filename)
                else:
                    print(f"文件{file.name}不是可接受的文件类型, 需要为 xlsx, xls 或 csv。")
                    error_msg.append(f"文件{file.name}不是可接受的文件类型, 需要为 xlsx, xls 或 csv。")
                    continue
            except Exception as e:
                print(f"读取文件出错，原因为{str(e)}")
                error_msg.append(f"读取文件{file.name}失败。")
                continue       
            
            # 对批量新增工单的文件的数据的头部进行格式检查，看是否有所有需要的项
            for item in constant.work_record_col_chinese_alias_map.keys():
                if item not in dataframe.columns:
                    print(f"{file.name}文件中缺少必要的列：{item}")
                    error_msg.append(f"{file.name}文件中缺少必要的列：{item}")
                    break
            # 说明在检测数据头部的时候格式不对
            if error_msg[i] != "": continue
            # 将不在work_record_col_chinese_alias_map中的列进行去除, 然后将中文的列名给弄成表的列名
            cols_to_keep = [col for col in dataframe.columns if col in constant.work_record_col_chinese_alias_map.keys()]
            dataframe = dataframe[cols_to_keep]
            dataframe.rename(columns=constant.work_record_col_chinese_alias_map, inplace=True)

            # 计算并生成fid列
            dataframe['fid'] = dataframe.apply(lambda row: hashlib.md5((str(row['createtime'])+"-"+str(row['agenname'])).encode("utf-8")).hexdigest(), axis=1)

            # 批量将数据进行插入到数据库            
            db = mysql_base.Db()
            db_result = db.group_insert_dataframe("workrecords_2023", dataframe)
            # 如果是成功插入，返回""， 进行list的第i个的占位，如果是失败插入，返回error，那么放进这个第i个的errorlist里面
            error_msg.append(db_result)

        # 将暂存的文件进行删除，连带这个目录进行删除
        try:
            shutil.rmtree(dir_path)
        except Exception as e:
            print(str(e))

        # 看是否有error
        has_error = any(item != "" for item in error_msg)
        if has_error:
            return JsonResponse({'status': 406, 'message': "批量导入失败。", 'data': error_msg}, json_dumps_params={'ensure_ascii': False}) 
        else:
            return JsonResponse({'status': 200, 'message': "批量导入成功。"}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'status': 405, 'message': "请求方法错误, 需要POST请求。"})

def work_record_update(request):
    if request.method == 'POST':
        work_record_detail_form = json.loads(request.body)

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if work_record_detail_form["registerDate"] <= "2023-12-31" and work_record_detail_form["solveDate"] >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        # 查询fid，暂且先通过登记日期和单位名称来
        fid = encryption_utils.md5_encryption(str(work_record_detail_form.get("registerDate")) + "-" + str(work_record_detail_form.get("agencyName")))

        try:
            work_record_service.update_work_record(fid, work_record_detail_form)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={ 'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data={'message': "更新成功!"}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要POST请求。"})

def work_record_delete(request):
    if request.method == 'POST':
        work_record_detail_form = json.loads(request.body)

        fid = encryption_utils.md5_encryption(str(work_record_detail_form.get("registerDate")) + "-" + str(work_record_detail_form.get("agencyName")))
        try:
            work_record_service.delete_work_record(fid, work_record_detail_form)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={ 'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'message': "删除成功!"}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要POST请求。"})

def work_record_init(request):
    """
    获取工单详细界面查询的初始配置，如一些问题分类的种类，出错功能有哪些功能等
    """
    if request.method == 'GET':
        data = {}

        db = mysql_base.Db()

        # 查询所有问题归属, 然后以 { party1: [xxx, xxx], party2:[xxx, xxx]}这样方式传给前端
        condition_dict = {
            # error_attribution 001代表的是问题归属的那个数据字典
            "t1.dictCode=":constant.data_dict_code_map["error_attribution"],
            "t2.dictCode=":constant.data_dict_code_map["error_attribution"],
            "t1.level=":1,
            "t2.level=":2,
        }
        problem_attribution_list = db.select([" t1.name as level1_name ", " t2.name as level2_name "],
                                        "work_record_data_dict t1 JOIN work_record_data_dict t2 ON t1.code = t2.parentCode",
                                        condition_dict, "")
        data["problemAttributionOptions"] = {}
        for item in problem_attribution_list:
            if data["problemAttributionOptions"].get(item["level1_name"]) is None:
                data["problemAttributionOptions"][item["level1_name"]] = []
            data["problemAttributionOptions"][item["level1_name"]].append(item["level2_name"])


        # 查询所有的问题分类
        condition_dict = {
            # error_type 002代表的是问题归属的那个数据字典
            "t1.dictCode=": constant.data_dict_code_map["error_type"],
            "t2.dictCode=": constant.data_dict_code_map["error_type"],
            "t1.level=": 1,
            "t2.level=": 2,
        }
        error_type_list = db.select([" t1.name as level1_name ", " t2.name as level2_name "],
                                             "work_record_data_dict t1 JOIN work_record_data_dict t2 ON t1.code = t2.parentCode",
                                             condition_dict, "")
        data["errorTypeOptions"] = {}
        for item in error_type_list:
            if data["errorTypeOptions"].get(item["level1_name"]) is None:
                data["errorTypeOptions"][item["level1_name"]] = []
            data["errorTypeOptions"][item["level1_name"]].append(item["level2_name"])


        # 查询所有产品类型
        condition_dict = {
            # product_type 003代表的是产品类型的那个数据字典
            "dictCode=": constant.data_dict_code_map["product_type"],
            "level=": 1
        }
        product_type_list = db.select(["name"], "work_record_data_dict", condition_dict, "")
        data["productTypeOptions"] = [ item["name"] for item in product_type_list]

        # 查询所有问题功能
        condition_dict = {
            # error_function是dict 004代表的是问题功能的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_function"],
            "level=": 1
        }
        error_function_list = db.select(["name"], "work_record_data_dict", condition_dict, "")
        data["errorFunctionOptions"] = [ item["name"] for item in error_function_list]

        # 查询所有问题因素
        condition_dict = {
            # error_type_factor 005代表的是问题因素的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_type_factor"],
            "level=": 2
        }
        error_factor_list = db.select(["name"], "work_record_data_dict", condition_dict, "")
        data["errorFactorOptions"] = [ item["name"] for item in error_factor_list]

        return JsonResponse(status=200, data=data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要POST请求。"} )