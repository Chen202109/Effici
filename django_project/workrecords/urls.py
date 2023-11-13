from django.urls import path

from . import views

urlpatterns = [
    #path('', views.workrecords),
    path('select',views.select),
    path('analysisselect',views.analysisselect),
    path('analysis_service_upgrade_trend',views.analysis_service_upgrade_trend),
    path('analysis_version_upgrade_trend',views.analysis_version_upgrade_trend),
    path('analysis_saas_function_by_province',views.analysis_saas_function_by_province),
    path('analysis_saas_function_by_province_agency',views.analysis_saas_function_by_province_agency),
]