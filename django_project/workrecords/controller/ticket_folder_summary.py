from workrecords.services import ticket_folder_summary_service
from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from django.http import JsonResponse

def analysis_customer_service_robot_summary(request):
    """
    分析票夹智能客服汇总数据
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        try:
            data = ticket_folder_summary_service.get_customer_service_robot_summary(begin_date, end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={"data":data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def analysis_customer_service_robot_matched_query_type_summary(request):
    """
    分析票夹智能客服的命中问答分类
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        try:
            data = ticket_folder_summary_service.get_customer_service_robot_matched_query_type_summary(begin_date, end_date)
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={"data":[{'seriesName': "命中问答数量", 'seriesData': data}]}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})