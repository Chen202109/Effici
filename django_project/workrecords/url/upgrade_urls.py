from django.urls import path

from workrecords.controller import upgrade_record_summary

urlpatterns = [
    path('analysis_saas_upgrade_problem_type', upgrade_record_summary.analysis_saas_upgrade_problem_type),
    path('analysis_saas_service_upgrade_trend', upgrade_record_summary.analysis_saas_service_upgrade_trend),
    path('analysis_saas_version_problem_by_resource_pool', upgrade_record_summary.analysis_saas_version_problem_by_resource_pool),
]