from django.urls import path

from workrecords.controller import views
from workrecords.controller import submit_workrecords
from workrecords.controller import workrecords_report
from workrecords.controller import workrecord_summary

urlpatterns = [

    path('work_record', submit_workrecords.work_record),
    path('work_record_group_add', submit_workrecords.work_record_group_add),
    path('work_record_update', submit_workrecords.work_record_update),
    path('work_record_delete', submit_workrecords.work_record_delete),
    path('work_record_init', submit_workrecords.work_record_init),

    path('analysisselect',workrecords_report.analysisselect),
    path('analysis_saas_problem_type_in_versions',workrecords_report.analysis_saas_problem_type_in_versions),
    path('analysis_select_new',workrecords_report.analysis_select_new),
    path('analysis_saas_problem_type_in_versions_new',workrecords_report.analysis_saas_problem_type_in_versions_new),
    path('analysis_saas_problem_type_detail_in_versions_new',workrecords_report.analysis_saas_problem_type_detail_in_versions_new),

    path('analysis_saas_upgrade_problem_type',views.analysis_saas_upgrade_problem_type),
    path('analysis_service_upgrade_trend',views.analysis_service_upgrade_trend),
    path('analysis_version_problem_by_resource_pool',views.analysis_version_problem_by_resource_pool),

    path('analysis_saas_large_problem_province_list',views.analysis_saas_large_problem_province_list),
    path('analysis_saas_large_problem_by_function_and_province',views.analysis_saas_large_problem_by_function_and_province),
    path('analysis_saas_large_problem_by_province',views.analysis_saas_large_problem_by_province),
    path('analysis_saas_large_problem_by_function',views.analysis_saas_large_problem_by_function),

    path('analysis_saas_monitor_province_list',views.analysis_saas_monitor_province_list),
    path('analysis_saas_monitor_problem_by_function_and_province',views.analysis_saas_monitor_problem_by_function_and_province),
    path('analysis_saas_monitor_problem_by_province',views.analysis_saas_monitor_problem_by_province),
    path('analysis_saas_minitor_problem_by_function',views.analysis_saas_minitor_problem_by_function),

    path('analysis_saas_added_service_province_list',views.analysis_saas_added_service_province_list),
    path('analysis_saas_added_service_by_function_and_province',views.analysis_saas_added_service_by_function_and_province),
    path('analysis_saas_added_service_by_province',views.analysis_saas_added_service_by_province),
    path('analysis_saas_added_service_by_function',views.analysis_saas_added_service_by_function),

    path('analysis_saas_problem_by_country', workrecord_summary.analysis_saas_problem_by_country),
    path('analysis_saas_problem_by_country_region', workrecord_summary.analysis_saas_problem_by_country_region),
    path('analysis_saas_function_by_province', workrecord_summary.analysis_saas_function_by_province),
    path('analysis_saas_problem_by_province_agency', workrecord_summary.analysis_saas_problem_by_province_agency),
    path('analysis_saas_problem_by_month', workrecord_summary.analysis_saas_problem_by_month),
    path('analysis_version_upgrade_trend', workrecord_summary.analysis_version_upgrade_trend),
    
    path('analysis_saas_privatization_license_register_province',views.analysis_saas_privatization_license_register_province),
]