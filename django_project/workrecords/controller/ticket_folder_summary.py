from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from workrecords.services import ticket_folder_summary_service
from django.http import JsonResponse

def analysis_ticket_folder_report_error_function_count(request):
    """
    电子票夹的数据分析界面，所选时间段内的出错功能与版本的对比总结表格
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        try:
            saas_problem_table_data = ticket_folder_summary_service.get_ticket_folder_report_error_function_count(begin_date,end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': saas_problem_table_data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_ticket_folder_report_problem_type_in_versions(request):
    """
    电子票夹的数据分析界面，所选时间段内的问题因素与版本的对比总结表格
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        try:
            data = ticket_folder_summary_service.get_ticket_folder_report_problem_type_in_versions(begin_date,end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_ticket_folder_report_problem_type_in_function_version(request):
    """
    电子票夹的数据分析界面，所选时间段内的问题因素与版本的对比总结表格
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        try:
            data = ticket_folder_summary_service.get_ticket_folder_report_problem_type_in_function_version(begin_date,end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_ticket_folder_report_problem_type_detail_in_versions(request):
    """
    电子票夹的数据分析界面，所选时间段内的问题因素与版本的对比总结表格
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        try:
            data = ticket_folder_summary_service.get_ticket_folder_report_problem_type_detail_in_versions(begin_date,end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(status=200, data={'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_ticket_folder_function_by_province(request):
    """
    分析省份受理的功能的问题数量的对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        function_names = request.GET.get('functionName').split(',')

        # 因为2023年和2024年是两个模板所以不能跨越这两个时间段查询，只能2023年查2023以前的，2024查2024以后的
        if begin_date <= "2023-12-31" and end_date >= "2024-01-01":
            return JsonResponse(status=400, data={'message': "因为是两个模板，请求时间不得跨越2023与2024年。"})

        try:
            data = ticket_folder_summary_service.get_ticket_folder_province_function_summary(begin_date, end_date, function_names)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data=data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})
