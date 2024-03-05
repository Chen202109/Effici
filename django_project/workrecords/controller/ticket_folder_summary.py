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