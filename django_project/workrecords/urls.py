from django.urls import path

from . import views

urlpatterns = [
    #path('', views.workrecords),
    path('select',views.select),
    path('analysisselect',views.analysisselect),
    path('analysis_saas_problem_type_in_versions',views.analysis_saas_problem_type_in_versions),
    path('analysis_service_upgrade_trend',views.analysis_service_upgrade_trend),
    path('analysis_version_problem_by_resource_pool',views.analysis_version_problem_by_resource_pool),
    path('analysis_version_upgrade_trend',views.analysis_version_upgrade_trend),
    path('analysis_saas_function_by_province',views.analysis_saas_function_by_province),
    path('analysis_saas_problem_by_province_agency',views.analysis_saas_problem_by_province_agency),
    path('analysis_saas_problem_by_month',views.analysis_saas_problem_by_month),
    
]