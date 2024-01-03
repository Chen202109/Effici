from django.shortcuts import render
from django.http import JsonResponse
from mydata import mysql_base
from workrecords.config import constant


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
        
        curr_page = int(request.GET.get('page', default='1'))
        curr_page_size = int(request.GET.get('pageSize', default='10'))

        detail = get_work_record_detail(search_filter, curr_page, curr_page_size)
        amount = get_work_record_count(search_filter)

        return JsonResponse({'data': detail, 'amount': amount}, json_dumps_params={'ensure_ascii': False})

    elif request.method == 'POST':
        work_record_detail_form = json.loads(request.body)

        hash_original = str(work_record_detail_form.get("registerDate"))+"-"+str(work_record_detail_form.get("agencyName"))
        md5 = hashlib.md5()
        md5.update(hash_original.encode("utf-8"))
        encrypted_data = md5.hexdigest()

        fieldDict = {}
        fieldDict["fid"] = encrypted_data

        # 进行别名的转换，转换成数据库里字段名
        for key, value in constant.work_record_col_alias_map.items():
            temp_value = work_record_detail_form.get(value)
            fieldDict[key] = "" if temp_value is None else temp_value
        
        db = mysql_base.Db()
        db.insert_copy("workrecords_2023", fieldDict)

        return JsonResponse({'data': "Adding successfully!"}, json_dumps_params={'ensure_ascii': False})


def work_record_group_add(request):
    if request.method == 'POST':
        error_msg=[]

        # 进行暂存上传文件的目录的创建
        try:
            dir_path = os.path.join(constant.MEDIA_ROOT, "111")
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        except:
            return JsonResponse({'status': 500, 'message': "服务端创建缓存文件夹失败。"}, json_dumps_params={'ensure_ascii': False})

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
                print(e)
                print(f"读取文件出错，原因为{e.message}")
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
            print(e.message)

        # 看是否有error
        has_error = has_error = any(item != "" for item in error_msg)
        if has_error:
            return JsonResponse({'status': 406, 'message': "批量导入失败。", 'data': error_msg}, json_dumps_params={'ensure_ascii': False}) 
        else:
            return JsonResponse({'status': 200, 'message': "批量导入成功。"}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'status': 405, 'message': "请求方法错误, 需要POST请求。"})

def work_record_update(request):
    if request.method == 'POST':
        work_record_detail_form = json.loads(request.body)

        hash_original = str(work_record_detail_form.get("registerDate"))+"-"+str(work_record_detail_form.get("agencyName"))
        md5 = hashlib.md5()
        md5.update(hash_original.encode("utf-8"))
        encrypted_data = md5.hexdigest()

        fieldDict = {}
        # 进行别名的转换，转换成数据库里字段名
        for key, value in constant.work_record_col_alias_map.items():
            if value == "registerDate": continue
            temp_value = work_record_detail_form.get(value)
            fieldDict[key] = "" if temp_value is None else temp_value
        
        print(f"wwwwwwww{fieldDict}")
        
        db = mysql_base.Db()
        db.update("workrecords_2023", fieldDict, {"fid=" : encrypted_data})

        return JsonResponse({'data': "Update successfully!"}, json_dumps_params={'ensure_ascii': False})
    

def work_record_delete(request):
    if request.method == 'POST':
        work_record_detail_form = json.loads(request.body)

        hash_original = str(work_record_detail_form.get("registerDate"))+"-"+str(work_record_detail_form.get("agencyName"))
        md5 = hashlib.md5()
        md5.update(hash_original.encode("utf-8"))
        encrypted_data = md5.hexdigest()

        db = mysql_base.Db()
        db.delete("workrecords_2023", {"fid=" : encrypted_data})

        return JsonResponse({'data': "Delete successfully!"}, json_dumps_params={'ensure_ascii': False})


def work_record_init(request):
    """
    获取工单详细界面查询的初始配置，如一些问题分类的种类，出错功能有哪些功能等
    """
    if request.method == 'GET':
        data = []
    return JsonResponse({'data': []}, json_dumps_params={'ensure_ascii': False})



def get_work_record_detail(search_filter, curr_page, curr_page_size):
    """
    获取搜索条件下的工单的详细信息，分页搜索
    """
    # 工单搜索条件
    isSolvedSql = "" if search_filter["isSolved"] == "" else f'AND issolve = "{search_filter["isSolved"]}"'
    errorFunctionSql = "" if search_filter["errorFunction"] == "" else f'AND errorfunction = "{search_filter["errorFunction"]}"'
    errorTypeSql = "" if search_filter["errorType"] == "" else f'AND errortype = "{search_filter["errorType"]}"'
    softVersionSql = "" if search_filter["softVersion"] == "" else f'AND softversion = "{search_filter["softVersion"]}"'
    problemDescriptionSql = "" if search_filter["problemDescription"] == "" else f'AND problem LIKE "%{search_filter["problemDescription"]}%"'

    db =mysql_base.Db()
    sql = f' SELECT {cat_all_work_record_table_cols_alias()} from workrecords_2023 ' \
            f' WHERE createtime>="{search_filter["beginData"]}" and createtime<="{search_filter["endData"]}" '\
            f' {isSolvedSql} {errorFunctionSql} {errorTypeSql} {softVersionSql} {problemDescriptionSql} '\
            f' ORDER BY createtime'
    results = db.select_offset(curr_page, curr_page_size, sql)
    return results


def get_work_record_count(search_filter):
    # 获取符合搜索的工单的总数
    if not search_filter['requestTotal']:
        return -1
    else:
        # 工单搜索条件
        condition_dict = {}
        condition_dict["createtime>="] = search_filter["beginData"]
        condition_dict["createtime<="] = search_filter["endData"]
        if search_filter["isSolved"] != "": condition_dict["issolve="] = search_filter["isSolved"]
        if search_filter["errorFunction"] != "": condition_dict["errorfunction="] = search_filter["errorFunction"]
        if search_filter["errorType"] != "": condition_dict["errortype="] = search_filter["errorType"]
        if search_filter["softVersion"] != "": condition_dict["softversion="] = search_filter["softVersion"]
        if search_filter["problemDescription"] != "": condition_dict["problem LIKE"] = "%"+search_filter["problemDescription"]+"%"

        db =mysql_base.Db()
        total_work_record_amount = db.select(["count(fid)"], "workrecords_2023", condition_dict, "")
        return total_work_record_amount
    

# --------------------------------------------------------------------- help functions ------------------------------------------------------

def cat_all_work_record_table_cols_alias():
    """
    select * from table 的情况下， 因为不想直接查询出现列名， 给所有列名起个别名
    """
    cat_alias_str = ''
    for key, value in constant.work_record_col_alias_map.items():
        cat_alias_str += f'{key} as {value}, '
    return cat_alias_str[:-2]

# --------------------------------------------------------------------- help functions ------------------------------------------------------