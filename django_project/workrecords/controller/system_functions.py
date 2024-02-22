import json

from workrecords.services import data_dict_service
from workrecords.exception.service.EfficiServiceException import EfficiServiceException
from django.http import JsonResponse


def data_dict_management_init(request):
    if request.method == 'GET':
        data_dict_list = data_dict_service.get_all_data_dict()
        data_dict_first = data_dict_service.get_data_dict_by_code(data_dict_list[0]["dictCode"]) if len(data_dict_list) > 0 else {}
        return JsonResponse( status=200, data={'dataDictList': data_dict_list, "dataDictFirst": data_dict_first}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def get_data_dict_detail(request):
    if request.method == 'GET':
        data_dict = data_dict_service.get_data_dict_by_code(request.GET.get('dictCode'))
        return JsonResponse( status=200, data={"dataDict": data_dict}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

def add_data_dict(request):
    if request.method == 'POST':
        add_data_dict_form = json.loads(request.body)
        try:
            data_dict = data_dict_service.add_data_dict(dict_name=add_data_dict_form["name"])
            return JsonResponse(status=200, data={"dataDict": data_dict}, json_dumps_params={'ensure_ascii': False})
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要POST请求。"})

def add_data_dict_record(request):
    if request.method == 'POST':
        add_data_dict_form = json.loads(request.body)
        try:
            data_dict = data_dict_service.add_data_dict_record(add_data_dict_form)
            return JsonResponse(status=200, data={"dataDict": data_dict}, json_dumps_params={'ensure_ascii': False})
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要POST请求。"})