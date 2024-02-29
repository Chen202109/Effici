from mydata import mysql_base
from django.http import JsonResponse

from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from workrecords.services import upgrade_summary_service
from workrecords.services import work_record_service
from workrecords.services.work_record_summary_service import get_work_record_resource_pool_error_function_summary


def analysis_saas_upgrade_problem_type(request):
    """
    分析升级数据和所属问题分类的对比
    """

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        try:
            data = upgrade_summary_service.get_upgrade_error_type_summary(begin_date, end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_service_upgrade_trend(request):
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        resource_pools = request.GET.get('resourcePool').split(',')
        function_names = request.GET.get('functionName').split(',')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        try:
            data = [{'service': f"{resource_pool}-{function_name}",
                     'data': upgrade_summary_service.get_service_upgrade_trend(begin_date, end_date, function_name, resource_pool)} for function_name
                    in function_names for resource_pool in resource_pools]
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_version_problem_by_resource_pool(request):
    """
    分析版本信息和bug的趋势对比。
    """

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        resource_pools = request.GET.get('resourcePool').split(',')
        function_names = request.GET.get('functionName').split(',')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        data = []

        try:
            # 先获取这段时间内的有哪些版本
            saas_version_data = work_record_service.get_work_record_distinct_version(begin_date, end_date, conditions={"softversion!=": "V3"})

            for resource_pool in resource_pools:
                # 根据错误功能进行查询，并且统计每个功能错误的数量
                data.extend(
                    get_work_record_resource_pool_error_function_summary(begin_date, end_date, resource_pool, function_names, saas_version_data))
                # 根据资源池查询筛选时间内这个资源池的日常升级和增值升级次数
                data.extend(upgrade_summary_service.get_upgrade_resource_pool_summary(begin_date, end_date, resource_pool, saas_version_data))
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})
