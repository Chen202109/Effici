from django.urls import path

from workrecords.controller import views
from workrecords.controller import system_functions
from workrecords.controller import submit_workrecords
from workrecords.controller import workrecord_summary, upgrade_record_summary,ticket_folder_summary

urlpatterns = [

    path('data_dict_management_init', system_functions.data_dict_management_init),
    path('get_data_dict_detail', system_functions.get_data_dict_detail),
    path('add_data_dict', system_functions.add_data_dict),
    path('add_data_dict_record', system_functions.add_data_dict_record),
    path('get_required_data_dict_record_for_work_record', system_functions.get_required_data_dict_record_for_work_record),

    path('work_record', submit_workrecords.work_record),
    path('work_record_group_add', submit_workrecords.work_record_group_add),
    path('work_record_update', submit_workrecords.work_record_update),
    path('work_record_delete', submit_workrecords.work_record_delete),

    path('analysis_saas_upgrade_problem_type',upgrade_record_summary.analysis_saas_upgrade_problem_type),
    path('analysis_saas_service_upgrade_trend',upgrade_record_summary.analysis_saas_service_upgrade_trend),
    path('analysis_saas_version_problem_by_resource_pool',upgrade_record_summary.analysis_saas_version_problem_by_resource_pool),
    path('analysis_ticket_folder_upgrade_problem_type',upgrade_record_summary.analysis_ticket_folder_upgrade_problem_type),

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
    path('analysis_report_problem_type_in_versions_new', workrecord_summary.analysis_report_saas_problem_type_in_versions_new),
    path('analysis_report_problem_type_detail_in_versions_new', workrecord_summary.analysis_report_saas_problem_type_detail_in_versions_new),
    path('analysis_report_problem_type_in_function_version_view_new', workrecord_summary.analysis_report_saas_problem_type_in_function_version_view_new),
    path('analysis_saas_problem_by_country', workrecord_summary.analysis_saas_problem_by_country),
    path('analysis_saas_problem_by_country_region', workrecord_summary.analysis_saas_problem_by_country_region),
    path('analysis_saas_function_by_province', workrecord_summary.analysis_saas_function_by_province),
    path('analysis_saas_problem_by_province_agency', workrecord_summary.analysis_saas_problem_by_province_agency),
    path('analysis_saas_problem_by_month', workrecord_summary.analysis_saas_problem_by_month),
    path('analysis_version_by_function', workrecord_summary.analysis_version_by_function),

    path('analysis_ticket_folder_report_error_function_count', ticket_folder_summary.analysis_ticket_folder_report_error_function_count),
    path('analysis_ticket_folder_report_problem_type_in_versions', ticket_folder_summary.analysis_ticket_folder_report_problem_type_in_versions),
    path('analysis_ticket_folder_report_problem_type_in_function_version', ticket_folder_summary.analysis_ticket_folder_report_problem_type_in_function_version),
    path('analysis_ticket_folder_report_problem_type_detail_in_versions', ticket_folder_summary.analysis_ticket_folder_report_problem_type_detail_in_versions),
    path('analysis_ticket_folder_function_by_province',
         ticket_folder_summary.analysis_ticket_folder_function_by_province),

]