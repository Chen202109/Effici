from workrecords.services import work_record_summary_service
from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from workrecords.services.data_dict_service import encode_data_item, decode_data_item
from django.http import JsonResponse
from workrecords.config import constant
from mydata import mysql_base
import pandas as pd
import copy
import time

def analysis_saas_problem_by_country(request):
    """
    分析每个省份的数据，给全国地图使用
    """

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        # 查询数据库的workrecord表然后所有region并放入数组中,因为是前端是echarts的地图，要求key的名字是name和value
        saas_province_problem_data = work_record_summary_service.get_work_record_province_summary(begin_date, end_date, region_alias="name", value_alias="value")
        # 对上线单位数量统计进行读取, 因为是地图，所以把key给改成name和value, 而不是柱状图的x和y
        saas_province_agency_account_data = pd.read_csv(constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_by_year_2023.csv",sep=',').rename(columns={'省份':'name','数量':'value'}).to_dict(orient="records")
        # 生成关于全国省份的数据
        data = work_record_summary_service.get_work_record_country_map_summary(saas_province_problem_data, saas_province_agency_account_data)

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_problem_by_country_region(request):
    """
    分析每个省份的数据统计，给全国地图周围的几张表使用
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        province = request.GET.get('province', default='全国')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        db =mysql_base.Db()

        # 对出错问题（开票，核销，数据同步等）进行查找，然后统计Top5
        saas_function_type_data = work_record_summary_service.get_work_record_error_function_summary(begin_date, end_date,province, db=db)
        sorted_saas_function_type_data = sorted(saas_function_type_data, key=lambda x : x['y'], reverse = True)[0:5]
        data.append([{'seriesName': province+"出错功能Top5", 'seriesData': sorted_saas_function_type_data}])

        # 对问题分类（实施配置，异常数据处理等）进行统计排序并找出前五
        saas_problem_type_data = work_record_summary_service.get_work_record_problem_type_summary(begin_date, end_date,province, db=db)
        sorted_saas_problem_type_data = sorted(saas_problem_type_data, key=lambda x : x['y'], reverse = True)[0:5]
        data.append([{'seriesName': province+"问题分类Top5", 'seriesData': sorted_saas_problem_type_data}])

        # 对生产监控异常的数据进行统计排序
        saas_monitor_problem_type_data = work_record_summary_service.get_monitor_problem_type_summary(begin_date, end_date, province, db=db)
        # 排序并找出前五, 因为前端使用横向柱状图，所以排序要反着来
        sorted_saas_monitor_problem_type_data = sorted(saas_monitor_problem_type_data, key=lambda x : x['y'], reverse = False)[-5:]
        data.append([{'seriesName': province+"生产监控问题分类Top5", 'seriesData': sorted_saas_monitor_problem_type_data}])

        # 对版本号和受理进行查询
        sorted_saas_version_data = work_record_summary_service.get_work_record_version_summary(begin_date, end_date, province, db=db)
        data.append([{'seriesName': province+"版本受理统计", 'seriesData': sorted_saas_version_data}])

        # 对产品分类（医疗，通用，高校等）进行统计
        agency_type_pie_gragh = work_record_summary_service.get_work_record_product_type_summary(begin_date, end_date, province, db=db)
        data.append(agency_type_pie_gragh)

        # 对重大故障的问题分类进行统计排序
        saas_large_problem_type_data = work_record_summary_service.get_large_problem_type_summary(begin_date, end_date, province, db=db)
        # 排序并找出前五, 这里reverse为false是因为前端使用的是横向的柱状图，他会把排序完的第一个的放在最底下，想要数值高的放在上方，reverse为false
        sorted_saas_large_problem_type_data = sorted(saas_large_problem_type_data, key=lambda x : x['y'], reverse = False)[-5:]
        data.append([{'seriesName': province+"私有化重大故障问题分类Top5", 'seriesData': sorted_saas_large_problem_type_data}])

        # 对summary的这些，单位开通数量，重大事故数量，license注册数量等进行数字的归纳
        saas_country_summary_table = work_record_summary_service.get_summary_item_amount(begin_date, end_date,province, db=db)
        data.append(saas_country_summary_table)

    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_function_by_province(request):
    """
    分析省份受理的功能的问题数量的对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        function_name = request.GET.get('functionName').split(',')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        try:
            data = work_record_summary_service.get_work_record_province_function_summary(begin_date, end_date, function_name)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_problem_by_province_agency(request):
    """
    分析省份受理的问题数量的对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        saas_province_problem_data = work_record_summary_service.get_work_record_province_summary(begin_date, end_date)
        data.append({'seriesName': "问题受理数量", 'seriesData': saas_province_problem_data})

        # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
        saas_large_problem_data = work_record_summary_service.get_large_problem_province_summary(begin_date, end_date)
        # 生成一个顺序与saas_province_problem_data一致的数组,如果重大故障查询的没有那个省份，则那个省份的y值为0，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
        saas_province_large_problem_data_inorder = [{'x': prov['x'], 'y': next((value['y'] for value in saas_large_problem_data if value['x'] == prov['x']), 0)} for prov in saas_province_problem_data]
        data.append({'seriesName': "私有化重大故障数量", 'seriesData': saas_province_large_problem_data_inorder})

        # 对上线单位数量统计进行读取
        saas_province_agency_account_data = pd.read_csv(constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_by_year_2023.csv",sep=',').rename(columns={'省份':'x','数量':'y'}).to_dict(orient="records")
        # 生成一个顺序与saas_province_problem_data一致的数组，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
        # 新数组的x值通过saas_province_problem_data获取，y的值通过dataFrame读取的上线单位的数量进行填入。
        # 如果是这一行报错StopIteration，基本上就是登记的时候省份没有登记对，比如内蒙古写成内蒙，需要去数据库进行调整让省份和constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_by_year_2023.csv"的省份名称一致
        saas_province_agency_account_data = [{**prov, 'y': next(filter(lambda ag: ag['x'] == prov['x'], saas_province_agency_account_data),{"y":0})['y']} for prov in saas_province_problem_data]
        data.append({'seriesName': "上线单位数量", 'seriesData': saas_province_agency_account_data})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_version_upgrade_trend(request):
    """
    分析版本信息和bug的趋势对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        province = request.GET.get('provinceSelected')
        function_name = request.GET.get('functionName').split(',')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        try:
            data = work_record_summary_service.get_work_record_version_function_summary(begin_date, end_date, province, function_name)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_saas_problem_by_month(request):
    """
    分析某一年月份受理的问题数量的对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        try:
            series_data = work_record_summary_service.get_work_record_month_summary(begin_date, end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        data.append({'seriesName': "问题受理数量", 'seriesData': series_data})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_work_record_report_error_function_count_old(request):

    # 判断请求类型
    if request.method == 'GET':
        # 获得GET请求后面的参数信息
        beginData = request.GET.get('beginData', default='2023-07-01')
        endData = request.GET.get('endData', default='2023-07-31')
        try:
            data = work_record_summary_service.get_work_record_error_function_count_old(beginData,endData)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_saas_problem_type_in_versions(request):
    """
    数据汇报界面的， 产品bug, 实施配置，异常数据处理，和各版本和功能的详细对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        try:
            data = work_record_summary_service.get_work_record_error_type_to_error_function_count_old(begin_date, end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})



def analysis_report_work_record_report_error_function_count_new(request):
    """
    数据汇报界面的， 新版本的，所选时间段内的出错功能与版本的对比总结表格
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')

        db = mysql_base.Db()

        condition_dict = {
            # error_function是dict 004代表的是问题功能的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_function"],
            "level=": 1
        }
        function_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

        condition_dict = {
            # error_type_factor 005代表的是问题因素的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_type_factor"],
            "level=": 1
        }
        error_factor_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

        # 开始查询生成出错功能和版本对比的表格数据
        sql = f'select softversion, errorfunction, count(*) as amount ' \
              f'from workrecords_2024 where createtime>="{begin_date}" and createtime<="{end_date}" ' \
              f'GROUP BY softversion, errorfunction'
        result = db.select_offset(1, 1000, sql)

        sql = f'select softversion, ' \
              f'count(case when errortypefactor between 10100 and 10200 then 1 else NULL end ) as 产品bug, ' \
              f'count(case when errortypefactor between 10200 and 10300 then 1 else NULL end ) as 异常数据处理, ' \
              f'count(case when errortypefactor between 10300 and 10400 then 1 else NULL end ) as 实施配置, ' \
              f'count(case when errortypefactor between 10400 and 10500 then 1 else NULL end ) as 需求, '\
              f'count(case when errortypefactor between 10500 and 10600 then 1 else NULL end ) as 其他 ' \
              f'from workrecords_2024 where createtime>="{begin_date}" and createtime<="{end_date}" ' \
              f'GROUP BY softversion'
        error_factor_result = db.select_offset(1, 1000, sql)

        saas_problem_table_data = []
        row_template = {"程序版本": "合计", "受理合计": 0}
        row_template.update({key["name"]:0 for key in function_list})
        row_template.update({key["name"]: 0 for key in error_factor_list})

        if len(result) == 0:
            saas_problem_table_data.append(row_template)
        else:
            # saas_problem_table_data
            row = copy.deepcopy(row_template)
            sum_row = copy.deepcopy(row_template)
            for i in range(len(result)):
                if row["程序版本"] != result[i]["softversion"]:
                    if i != 0:
                        # 到了不同版本了,添加产品bug等错误因素信息添加，存入数据saas_problem_table_data，新开一行
                        error_factor_row = next(item for item in error_factor_result if item.get("softversion") == row["程序版本"])
                        for key in error_factor_list:
                            row.update({key["name"]: error_factor_row[key["name"]]})
                            sum_row.update({key["name"]: sum_row[key["name"]]+error_factor_row[key["name"]]})
                        saas_problem_table_data.append(row)
                        row = copy.deepcopy(row_template)
                    row["程序版本"] = result[i]["softversion"]
                # 进行对应的版本errorfunction数量添加和合计累计
                row[result[i]["errorfunction"]] += result[i]["amount"]
                row["受理合计"] += result[i]["amount"]
                sum_row[result[i]["errorfunction"]] += result[i]["amount"]
                sum_row["受理合计"] += result[i]["amount"]
            # 最后一行，因为循环到结尾，没有添加，这里添加最后一行version, 然后添加上合计栏
            error_factor_row = next(item for item in error_factor_result if item.get("softversion") == row["程序版本"])
            for key in error_factor_list:
                row.update({key["name"]: error_factor_row[key["name"]]})
                sum_row.update({key["name"]: sum_row[key["name"]] + error_factor_row[key["name"]]})
            saas_problem_table_data.append(row)
            saas_problem_table_data.append(sum_row)

        return JsonResponse(status=200, data={'data': saas_problem_table_data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_saas_problem_type_in_versions_new(request):
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected')

        db = mysql_base.Db()
        condition_dict = {}
        condition_dict["createtime>="] = begin_date
        condition_dict["createtime<="] = end_date
        if party_selected != "全部":
            party_encoded = encode_data_item(party_selected, constant.data_dict_code_map["error_attribution"])
            # 10^3 是因为party的二级现在是3位数，所以是10^3
            condition_dict["belong>="] = party_encoded * 1000
            condition_dict["belong<"] = (party_encoded + 1) * 1000
        result = db.select(["errortypefactor", "softversion", "count(*) as amount"], "workrecords_2024", condition_dict,
                           "GROUP BY errortypefactor, softversion")
        version_list = sorted(set(item["softversion"].replace(".", "_") for item in result))

        # 要处理成这样的类型给前端渲染 [{"问题因素": "产品bug", "V4_3_2_1":3},{"问题因素": "实施配置", }]
        error_factor_col1_table = []
        error_factor_col2_table = []
        data = [{"problem":"问题因素", "problemData": error_factor_col1_table},{"problem":"问题因素(细)", "problemData": error_factor_col2_table}]

        for item in result :
            error_factor = decode_data_item(item["errortypefactor"], constant.data_dict_code_map["error_type_factor"]).split("-")
            error_factor_col1 = error_factor[0]
            error_factor_col2 = error_factor[1]
            version = item["softversion"].replace(".", "_")
            amount = item["amount"]

            # 去找是否有登记过这个因素
            error_factor_col1_label = "问题因素" if party_selected == "全部" else f"{party_selected}-问题因素"
            error_factor_col2_label = "问题因素(细)" if party_selected == "全部" else f"{party_selected}-问题因素(细)"
            insert_version_into_list(error_factor_col1_table, error_factor_col1_label, error_factor_col1, version_list, version, amount, "合计")
            insert_version_into_list(error_factor_col2_table, error_factor_col2_label, error_factor_col2, version_list, version, amount, "合计")

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=200, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_saas_problem_type_in_function_version_view_new(request):
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected')

        data = []

        db = mysql_base.Db()

        condition_dict = {
            # error_function是dict 004代表的是问题功能的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_function"],
            "level=": 1
        }
        error_function_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

        condition_dict = {
            # error_type_factor 005代表的是问题因素的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_type_factor"],
            "level=": 1
        }
        error_factor_list = db.select(["code, name"], "work_record_data_dict", condition_dict, "")

        for error_factor_col1 in error_factor_list:
            # 将版本号里的"."转换成"_"，因为前端el-table的表头里如果字符串是带点的话会消失
            sql = f'SELECT replace(softversion,".","_") as softversion'
            for function in error_function_list:
                sql += f', SUM(IF(`errorfunction`="{function["name"]}",amount,0)) AS {function["name"]} '
            sql += ' FROM '
            sql += ' (SELECT softversion , errorfunction, errortypefactor, count(*) as amount '
            sql += ' FROM workrecords_2024 '
            sql += f' WHERE createtime>="{begin_date}" AND createtime<="{end_date}" '
            sql += f' AND errortypefactor >= {error_factor_col1["code"] * 100} AND errortypefactor <= { (error_factor_col1["code"]+1) * 100}'
            sql += ' GROUP BY softversion, errorfunction, errortypefactor ) A '
            sql += ' GROUP BY softversion '
            result = db.select_offset(1, 2000, sql)

            # 查询出来的结果像是[{'softversion': 'V4_3_1_3', '开票功能': Decimal('0'), '收缴业务': Decimal('0'), ...}, {...}]
            # 进行行列翻转
            saas_problem_type_and_function_data_in_version = []
            for function in error_function_list:
                new_item = {error_factor_col1["name"]: function["name"]}
                total = 0
                for item in result:
                    new_item[item["softversion"]] = int(item[function["name"]])
                    total += int(item[function["name"]])
                new_item["合计"] = total
                saas_problem_type_and_function_data_in_version.append(new_item)

            data.append({"problem":error_factor_col1["name"],"problemData":saas_problem_type_and_function_data_in_version})

        return JsonResponse({'status': 200, 'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'status': 405, 'message': "请求方法错误, 需要GET请求。"})

def analysis_report_saas_problem_type_detail_in_versions_new(request):
    """
    数据汇报界面的， 新版本的，问题分类和各版本和功能的详细对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected')

        db = mysql_base.Db()

        data = []

        condition_dict = {}
        condition_dict["createtime>="] = begin_date
        condition_dict["createtime<="] = end_date
        if party_selected != "全部":
            party_encoded = encode_data_item(party_selected, constant.data_dict_code_map["error_attribution"])
            # 10^3 是因为party的二级现在是3位数，所以是10^3
            condition_dict["belong>="] = party_encoded * 1000
            condition_dict["belong<"] = (party_encoded + 1) * 1000
        result = db.select(["errortypefactor", "softversion", "errortype", "count(*) as amount"], "workrecords_2024", condition_dict,
                           "GROUP BY errortypefactor, softversion, errortype")
        print(f"workrecord 2024 table result : {result}")
        version_list = sorted(set(item["softversion"].replace(".", "_") for item in result))

        # 转化成前端可以直接渲染上el-table的形式,格式像这样
        # [{'异常数据处理': '报表功能', 'V3': 1, 'V4_3_1_2': 0, 'V4_3_1_3': 0, 'V4_3_2_0': 2, 'V4_3_2_1': 0}, {...}]
        error_factor_col1_list = {}
        after_time = time.time()
        for item in result:
            # 获取errorfactor大类的decode，如产品bug，实施配置等， errorfactor的码去掉后面两位的小类的编码所以除以100
            error_factor_col1_decoded = decode_data_item(int(item["errortypefactor"] / 100), constant.data_dict_code_map["error_type_factor"])
            error_type_decoded = decode_data_item(item["errortype"], constant.data_dict_code_map["error_type"])
            # 因为前端的el-table的表头如果字符串带'.'会失效，转换成"_"传给前端
            version = item["softversion"].replace(".", "_")
            amount = item["amount"]

            # 如果data里面还没有这一项errorfactor大类，添加这一个项目的字典，并且记录下这个在data中的index
            if error_factor_col1_list.get(error_factor_col1_decoded) is None:
                error_factor_col1_list[error_factor_col1_decoded] = len(data)
                data.append({
                    "problemParty": party_selected,
                    "problemType": error_factor_col1_decoded,
                    "problemData": []
                })

            # 从data中找到这一项errorfactor大类对应的问题分类的列表
            problem_data = data[error_factor_col1_list[error_factor_col1_decoded]]["problemData"]
            problem_data_func_label = error_factor_col1_decoded if party_selected == "全部" else f"{party_selected}-{error_factor_col1_decoded}"
            insert_version_into_list(problem_data, problem_data_func_label, error_type_decoded, version_list, version, amount, "合计")

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def insert_version_into_list(list, label_key, label_value, version_list, version, amount, summary_row_label):
    """
    当需要数据结构为 [ {错误标签: 错误1, 版本号1: 错误数量, 版本号2: 错误数量, ... , 合计: 合计错误数量}, {...}, {...} ]
    想往里面插入一个错误的版本号的错误数量信息。
    :param list: 错误列表, 里面的元素是字典
    :param label_key: 错误标签，代表这个错误列表是关于什么错误的
    :param label_value: 错误标签的值，代表这个错误列表里的某个元素字典里面存放的数据是关于什么错误的
    :param version_list: 版本号的列表
    :param version: 需要插入的那个错误的版本号
    :param amount: 需要插入的那个错误的版本号的错误数量
    :param summary_row_label: 合计栏的标签，一般为"合计"
    """
    error_item_index = None
    for index, item in enumerate(list):
        # 如果这个错误已经在这个错误列表中登记过，返回这个错误所在的字典元素的位置
        if label_key in item and item[label_key] == label_value:
            error_item_index = index
    if error_item_index is None:
        # 放入该问题标签(如问题分类)和问题名字(如实施配置,异常数据处理等)，然后放入所有的查询结果的version
        new_error_factor_col1_dict = {label_key: label_value}
        new_error_factor_col1_dict.update({v: 0 for v in version_list})
        new_error_factor_col1_dict[summary_row_label] = amount
        new_error_factor_col1_dict[version] = amount
        list.append(new_error_factor_col1_dict)
    else:
        # 往版本字典添加更新错误数量
        list[error_item_index][version] += amount
        list[error_item_index][summary_row_label] += amount