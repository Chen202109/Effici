from django.urls import path

from workrecords.controller import ticket_folder_summary

urlpatterns = [
    path('analysis_customer_service_robot_summary', ticket_folder_summary.analysis_customer_service_robot_summary),
    path('analysis_customer_service_robot_matched_query_type_summary', ticket_folder_summary.analysis_customer_service_robot_matched_query_type_summary),
]