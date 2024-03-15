from workrecords.services import work_record_summary_service
from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from django.http import JsonResponse
from workrecords.config import constant
from mydata import mysql_base
import pandas as pd

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

        try:
            # 查询数据库的workrecord表然后所有region并放入数组中,因为是前端是echarts的地图，要求key的名字是name和value
            saas_province_problem_data = work_record_summary_service.get_work_record_province_summary(begin_date, end_date, region_alias="name",
                                                                                                      value_alias="value")
            # 对上线单位数量统计进行读取, 因为是地图，所以把key给改成name和value, 而不是柱状图的x和y
            saas_province_agency_account_data = pd.read_csv(constant.AGENCY_ACCOUNT_FILE_ROOT + "agency_account_total.csv", sep=',').rename(
                columns={'省份': 'name', '数量': 'value'}).to_dict(orient="records")
            # 生成关于全国省份的数据
            data = work_record_summary_service.get_work_record_country_map_summary(saas_province_problem_data, saas_province_agency_account_data)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        return JsonResponse(status=200, data=data, json_dumps_params={'ensure_ascii': False})
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

        try:
            db = mysql_base.Db()

            # 对出错问题（开票，核销，数据同步等）进行查找，然后统计Top5
            saas_function_type_data = work_record_summary_service.get_work_record_error_function_summary(begin_date, end_date, province, db=db)
            sorted_saas_function_type_data = sorted(saas_function_type_data, key=lambda x: x['y'], reverse=True)[0:5]
            data.append([{'seriesName': province + "出错功能Top5", 'seriesData': sorted_saas_function_type_data}])

            # 对问题分类（实施配置，异常数据处理等）进行统计排序并找出前五
            saas_problem_type_data = work_record_summary_service.get_work_record_problem_type_summary(begin_date, end_date, province, db=db)
            sorted_saas_problem_type_data = sorted(saas_problem_type_data, key=lambda x: x['y'], reverse=True)[0:5]
            data.append([{'seriesName': province + "问题分类Top5", 'seriesData': sorted_saas_problem_type_data}])

            # 对生产监控异常的数据进行统计排序
            saas_monitor_problem_type_data = work_record_summary_service.get_monitor_problem_type_summary(begin_date, end_date, province, db=db)
            # 排序并找出前五, 因为前端使用横向柱状图，所以排序要反着来
            sorted_saas_monitor_problem_type_data = sorted(saas_monitor_problem_type_data, key=lambda x: x['y'], reverse=False)[-5:]
            data.append([{'seriesName': province + "生产监控问题分类Top5", 'seriesData': sorted_saas_monitor_problem_type_data}])

            # 对版本号和受理进行查询
            sorted_saas_version_data = work_record_summary_service.get_work_record_version_summary(begin_date, end_date, province, db=db)
            data.append([{'seriesName': province + "版本受理统计", 'seriesData': sorted_saas_version_data}])

            # 对产品分类（医疗，通用，高校等）进行统计
            agency_type_pie_gragh = work_record_summary_service.get_work_record_product_type_summary(begin_date, end_date, province, db=db)
            data.append(agency_type_pie_gragh)

            # 对重大故障的问题分类进行统计排序
            saas_large_problem_type_data = work_record_summary_service.get_large_problem_type_summary(begin_date, end_date, province, db=db)
            # 排序并找出前五, 这里reverse为false是因为前端使用的是横向的柱状图，他会把排序完的第一个的放在最底下，想要数值高的放在上方，reverse为false
            sorted_saas_large_problem_type_data = sorted(saas_large_problem_type_data, key=lambda x: x['y'], reverse=False)[-5:]
            data.append([{'seriesName': province + "私有化重大故障问题分类Top5", 'seriesData': sorted_saas_large_problem_type_data}])

            # 对summary的这些，单位开通数量，重大事故数量，license注册数量等进行数字的归纳
            saas_country_summary_table = work_record_summary_service.get_summary_item_amount(begin_date, end_date, province, db=db)
            data.append(saas_country_summary_table)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_function_by_province(request):
    """
    分析省份受理的功能的问题数量的对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        function_name = request.GET.get('functionName').split(',')
        system_label = request.GET.get('systemLabel')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        try:
            data = work_record_summary_service.get_work_record_province_function_summary(begin_date, end_date, function_name, system_label)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data=data, json_dumps_params={'ensure_ascii': False})
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

        try:
            # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
            if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
                return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

            # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]
            saas_province_problem_data = work_record_summary_service.get_work_record_province_summary(begin_date, end_date)
            data.append({'seriesName': "问题受理数量", 'seriesData': saas_province_problem_data})

            # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
            saas_large_problem_data = work_record_summary_service.get_large_problem_province_summary(begin_date, end_date)
            # 生成一个顺序与saas_province_problem_data一致的数组,如果重大故障查询的没有那个省份，则那个省份的y值为0，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
            saas_province_large_problem_data_inorder = [
                {'x': prov['x'], 'y': next((value['y'] for value in saas_large_problem_data if value['x'] == prov['x']), 0)} for prov in
                saas_province_problem_data]
            data.append({'seriesName': "私有化重大故障数量", 'seriesData': saas_province_large_problem_data_inorder})

            # 对上线单位数量统计进行读取
            saas_province_agency_account_data = pd.read_csv(constant.AGENCY_ACCOUNT_FILE_ROOT + "agency_account_total.csv", sep=',').rename(
                columns={'省份': 'x', '数量': 'y'}).to_dict(orient="records")
            # 生成一个顺序与saas_province_problem_data一致的数组，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
            # 新数组的x值通过saas_province_problem_data获取，y的值通过dataFrame读取的上线单位的数量进行填入。
            # 如果是这一行报错StopIteration，基本上就是登记的时候省份没有登记对，比如内蒙古写成内蒙，需要去数据库进行调整让省份和constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_total.csv"的省份名称一致
            saas_province_agency_account_data = [
                {**prov, 'y': next(filter(lambda ag: ag['x'] == prov['x'], saas_province_agency_account_data), {"y": 0})['y']} for prov in
                saas_province_problem_data]
            data.append({'seriesName': "上线单位数量", 'seriesData': saas_province_agency_account_data})
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_version_by_function(request):
    """
    分析版本信息和出错功能的趋势对比。
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
        system_label = request.GET.get('systemLabel')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})
        try:
            series_data = work_record_summary_service.get_work_record_month_summary(begin_date, end_date, system_label)
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
        begin_date = request.GET.get('beginData', default='2023-07-01')
        end_date = request.GET.get('endData', default='2023-07-31')
        try:
            data = work_record_summary_service.get_work_record_error_function_count_old(begin_date,end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data=data, json_dumps_params={'ensure_ascii': False})
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
        system_label = request.GET.get('systemLabel')

        try:
            saas_problem_table_data = work_record_summary_service.get_work_record_report_error_function_count_new(begin_date,end_date, system_label)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': saas_problem_table_data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_work_record_problem_type_in_versions_new(request):
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected',default="全部")
        system_label = request.GET.get('systemLabel', default=None)
        try:
            data = work_record_summary_service.get_work_record_report_problem_type_in_versions_new(begin_date, end_date, party_selected, system_label)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=200, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_work_record_problem_type_detail_in_versions_new(request):
    """
    数据汇报界面的， 新版本的，问题分类和各版本和功能的详细对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected', default="全部")
        system_label = request.GET.get('systemLabel', default=None)

        try:
            data = work_record_summary_service.get_work_record_report_problem_type_detail_in_versions_new(begin_date, end_date, party_selected, system_label)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_report_work_record_problem_type_in_function_version_view_new(request):
    """
        数据汇报界面的， 新版本的，问题分类和各版本和功能的详细对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected')
        system_label = request.GET.get('systemLabel', default=None)
        try:
            data = work_record_summary_service.get_work_record_report_problem_type_in_function_version_view_new(begin_date, end_date, party_selected, system_label)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

