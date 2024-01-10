
from mydata import mysql_base
import pandas as pd
import datetime

table_name = "work_record_data_dict"

def add_data_dict(dict):
    return 

def group_add_data_dict(file_path, filename):
    error_msg = ""

    # 只允许xlsx, xls 文件
    file_extension = filename.split('.')[-1]
    if file_extension == 'xlsx' or file_extension == 'xls': 
        dataframe = pd.read_excel(io=file_path, header=0)
    else:
        error_msg = f"文件{filename}不是可接受的文件类型, 需要为 xlsx, xls 或 csv。"


    # 对文件进行读取, 因为pandas读excel,会默认将空的格子读成NaN,将读出来的col里面为NaN的值去除
    error_attribution = [x for x in dataframe["问题归属"] if pd.isna(x)==False]

    error_type = [x for x in dataframe["问题分类"] if pd.isna(x)==False]

    product_type = [x for x in dataframe["产品类型"] if pd.isna(x)==False]
    insert_data = update_product_type_data_dict(product_type)

    # 转成dataframe，列名为字典编码，条目编码，层级，父级条目编码，条目名，启用时间， 关闭时间, 是否启用
    insert_dataframe = pd.DataFrame(insert_data,columns=['fid', 'dictCode', 'code', 'level', 'parentCode', 'name', 'enableTime', 'disableTime', 'enable'])

    db =mysql_base.Db()
    result = db.bench_save(table_name, insert_dataframe)


def delete_data_dict(dict):
    return


def update_error_attribution_data_dict(error_attribution_new):
    print(error_attribution_new)
    dict_code = "001"
    error_attribution_old = get_data_dict(dict_code)
    for item in error_attribution_new:
        attribution_party_new = item.split('-')

    return


def update_error_type_data_dict(error_type_new):
    print(error_type_new)
    dict_code = "002"
    error_type_old = get_data_dict(dict_code)
    print(error_type_old)

    is_empty = len(error_type_old) == 0
    update_data = []
    insert_data = []

    for new_item in error_type_new:
        error_function_new = new_item.split('-')
        error_function_new_col_1 = error_function_new[0]
        error_function_new_col_2 = error_function_new[1]
        error_function_new_col_3 = error_function_new[2]

        parent_code = None

        for old_item in error_type_old:
            if old_item["level"] == 1 and error_function_new_col_1 == old_item["name"] :
                # 找到匹配的第一个选项
                parent_code = old_item["code"]
                print("更新")
                break
        # 没有匹配到，说明以前没有这个条目，新增
        print("新增")


        

    return


def update_product_type_data_dict(product_type_new):
    print(product_type_new)
    dict_code = "004"
    product_type_old = get_data_dict(dict_code)
    print(product_type_old)
    
    is_empty = len(product_type_old) == 0
    is_insert = True
    # 需要注入或者更新的数据， 格式为 字典编码，条目编码，层级，父级条目编码，条目名，启用时间， 关闭时间, 是否启用
    insert_data = []

    fid = 10041001

    for new_item in product_type_new:
        if not is_empty:
            for old_item in product_type_old:
                if new_item == old_item["name"]:
                    #  因为productType只有一层，name匹配到了就说明是原来数据库就存在的, 
                    # 那么只用找到那一条，将enable变成1,将endtime清空
                    insert_data.append([old_item['fid'], dict_code, old_item["code"], old_item["level"], old_item["parentCode"], new_item, datetime.date.today(), None, 1])
                    is_insert = False
                    break
        if is_insert:
            # 没有找到，需要新增
            insert_data.append([fid, dict_code, "001", 1, None, new_item, datetime.date.today(), None, 1])
            fid = fid + 1
        is_insert = True       

    return insert_data


def encode_data_item(item, dict_code):
    """
    将传入的数据字典条目在指定的数据字典查询编码， 查询成功返回编码。
    """
    item_cols = item.split("-")
    db =mysql_base.Db()
    # 因为第一层是null 
    parent_code = None
    for i in range(len(item_cols)):
        condition_dict = {}
        condition_dict["dictCode="] = dict_code
        condition_dict["level="] = i+1
        condition_dict["name="] = item_cols[i]
        condition_dict["parentCode="] = parent_code
        parent_code = db.select(["code"], table_name, condition_dict, "")
        print(f"parent code is : {parent_code}")
    return parent_code

    

def decode_data_item(item_code, dict_code):
    """
    传入条目编码, 查询对应的路径
    """
    item = ""
    db =mysql_base.Db()
    parent_code = item_code
    while parent_code is not None:
        condition_dict = {}
        condition_dict["dictCode="] = dict_code
        condition_dict["code="] = parent_code
        node = db.select(["name", "parentCode"], table_name, condition_dict, "")
        print(f"node is {node}")
        parent_code = node[0]["parentCode"]
        item = node[0]['name'] +"-" + item
    return item[:-1]



def get_data_dict(dict_code):
    db =mysql_base.Db()
    condition_dict = {}
    condition_dict["dictCode="] = dict_code
    data_dict_old = db.select("*", table_name, condition_dict, "")
    return data_dict_old