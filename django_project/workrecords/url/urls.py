from django.urls import path
from django.urls import include

from workrecords.controller import views
from workrecords.controller import submit_workrecords
from workrecords.controller import workrecord_summary

urlpatterns = [

    path('work_record', submit_workrecords.work_record),
    path('work_record_group_add', submit_workrecords.work_record_group_add),
    path('work_record_update', submit_workrecords.work_record_update),
    path('work_record_delete', submit_workrecords.work_record_delete),

    path('analysis_saas_privatization_license_register_province',views.analysis_saas_privatization_license_register_province),

    path('get_saas_large_problem_province_list',views.get_saas_large_problem_province_list),
    path('analysis_saas_large_problem_by_type_and_province',views.analysis_saas_large_problem_by_type_and_province),
    path('analysis_saas_large_problem_by_province',views.analysis_saas_large_problem_by_province),
    path('analysis_saas_large_problem_by_type',views.analysis_saas_large_problem_by_type),

    path('get_saas_monitor_province_list',views.get_saas_monitor_province_list),
    path('analysis_saas_monitor_problem_by_type_and_province',views.analysis_saas_monitor_problem_by_type_and_province),
    path('analysis_saas_monitor_problem_by_province',views.analysis_saas_monitor_problem_by_province),
    path('analysis_saas_minitor_problem_by_type',views.analysis_saas_minitor_problem_by_type),

    path('get_saas_added_service_province_list',views.get_saas_added_service_province_list),
    path('analysis_saas_added_service_by_type_and_province',views.analysis_saas_added_service_by_type_and_province),
    path('analysis_saas_added_service_by_province',views.analysis_saas_added_service_by_province),
    path('analysis_saas_added_service_by_type',views.analysis_saas_added_service_by_type),

    path('analysis_report_work_record_report_error_function_count_old',workrecord_summary.analysis_report_work_record_report_error_function_count_old),
    path('analysis_report_saas_problem_type_in_versions', workrecord_summary.analysis_report_saas_problem_type_in_versions),
    path('analysis_report_work_record_report_error_function_count_new', workrecord_summary.analysis_report_work_record_report_error_function_count_new),
    path('analysis_report_work_record_problem_type_in_versions_new', workrecord_summary.analysis_report_work_record_problem_type_in_versions_new),
    path('analysis_report_work_record_problem_type_detail_in_versions_new', workrecord_summary.analysis_report_work_record_problem_type_detail_in_versions_new),
    path('analysis_report_work_record_problem_type_in_function_version_view_new', workrecord_summary.analysis_report_work_record_problem_type_in_function_version_view_new),
    path('analysis_saas_problem_by_country', workrecord_summary.analysis_saas_problem_by_country),
    path('analysis_saas_problem_by_country_region', workrecord_summary.analysis_saas_problem_by_country_region),
    path('analysis_saas_function_by_province', workrecord_summary.analysis_saas_function_by_province),
    path('analysis_saas_problem_by_province_agency', workrecord_summary.analysis_saas_problem_by_province_agency),
    path('analysis_saas_problem_by_month', workrecord_summary.analysis_saas_problem_by_month),
    path('analysis_version_by_function', workrecord_summary.analysis_version_by_function),

    path('system/',include('workrecords.url.system_management_urls')),
    path('upgrade/',include('workrecords.url.upgrade_urls')),
    path('ticket_folder/',include('workrecords.url.ticket_folder_urls')),
]