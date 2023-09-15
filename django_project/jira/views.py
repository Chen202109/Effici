from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def jira(request):
    reStrtree=[['专利局','张三'],['福建省','李四']]
    return HttpResponse(reStrtree)