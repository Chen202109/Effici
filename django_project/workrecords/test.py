import os
import workrecords.services.data_dict_service as data_dict_service

from django.test import TestCase


class TestModule1(TestCase):
    
    # def test_data_dict(self):
    #     print("test group add data dict !!")
    #     media_root = r"E:\myWork\Effici\django_project\media_files\workrecords"
    #     filename = "2024年_SaaS受理工时统计表.xlsx"
    #     path = os.path.join(media_root, filename)
    #     data_dict_service.group_add_data_dict(path, filename)
    

    # def test_data_dict_1(self):
    #     print("test encode dict !!")
    #     item = "反算功能-同步开票点-数据反算"
    #     result = data_dict_service.encode_data_item(item, "002")
    #     print(f"test encode dict result is {result}")


    # def test_data_dict_2(self):
    #     print("test decode dict !!")
    #     item = "0010001001"
    #     result = data_dict_service.decode_data_item(item, "002")
    #     print(f"test decode dict result is {result}")

    def test_data_dict_3(self):
        item = "单位断电"
        result = data_dict_service.encode_single_item(item, "001")
        print(f"test decode dict result is {result}")
        print(f"test deocde result type is {type(result)}")

if __name__ == '__main__':
    pass