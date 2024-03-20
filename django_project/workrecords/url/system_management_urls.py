from django.urls import path

from workrecords.controller import system_functions

urlpatterns = [
    path('data_dict_management_init', system_functions.data_dict_management_init),
    path('get_data_dict_detail', system_functions.get_data_dict_detail),
    path('add_data_dict', system_functions.add_data_dict),
    path('add_data_dict_record', system_functions.add_data_dict_record),
    path('get_required_data_dict_record_for_work_record', system_functions.get_required_data_dict_record_for_work_record),
]