from mydata import mysql_base
from workrecords.config import constant
from workrecords.services import data_dict_service

def get_work_record_detail(search_filter, curr_page, curr_page_size):
    """
    获取搜索条件下的工单的详细信息，分页搜索
    """
    # 工单搜索条件
    table_name = "workrecords_2024" if search_filter["beginData"] >= "2024-01-01" else "workrecords_2023"
    is_solved_sql = "" if search_filter["isSolved"] == "" else f'AND issolve = "{search_filter["isSolved"]}"'
    error_function_sql = "" if search_filter["errorFunction"] == "" else f'AND errorfunction = "{search_filter["errorFunction"]}"'
    soft_version_sql = "" if search_filter["softVersion"] == "" else f'AND softversion = "{search_filter["softVersion"]}"'
    problem_description_sql = "" if search_filter["problemDescription"] == "" else f'AND problem LIKE "%{search_filter["problemDescription"]}%"'

    error_type_sql = "" if search_filter["errorType"] == "" else f'AND errortype = "{search_filter["errorType"]}"'

    db =mysql_base.Db()
    sql = f' SELECT {cat_all_work_record_table_cols_alias()} from {table_name} ' \
            f' WHERE createtime>="{search_filter["beginData"]}" and createtime<="{search_filter["endData"]}" '\
            f' {is_solved_sql} {error_function_sql} {error_type_sql} {soft_version_sql} {problem_description_sql} '\
            f' ORDER BY createtime'
    results = db.select_offset(curr_page, curr_page_size, sql)

    # 如果是新版本的工单记录模板，因为问题分类,问题归属是编码，所以进行转码
    if search_filter["beginData"] >= "2024-01-01":
        for item in results:
            error_attribution =data_dict_service.decode_data_item(item["problemAttribution"], constant.data_dict_code_map["error_attribution"])
            item["problemAttribution"] = error_attribution
            error_type = str(data_dict_service.decode_data_item(item["problemType"], constant.data_dict_code_map["error_type"]))
            error_factor_col2 = str(data_dict_service.decode_data_item(item["problemFactor"], constant.data_dict_code_map["error_type_factor"])).split("-")[1]
            item["problemType"] = f"{error_type}-{error_factor_col2}"
            item.pop("problemFactor")
    return results

def get_work_record_count(search_filter):
    # 获取符合搜索的工单的总数
    if not search_filter['requestTotal']:
        return -1
    else:
        # 工单搜索条件
        condition_dict = {}
        condition_dict["createtime>="] = search_filter["beginData"]
        condition_dict["createtime<="] = search_filter["endData"]
        if search_filter["isSolved"] != "": condition_dict["issolve="] = search_filter["isSolved"]
        if search_filter["errorFunction"] != "": condition_dict["errorfunction="] = search_filter["errorFunction"]
        if search_filter["errorType"] != "": condition_dict["errortype="] = search_filter["errorType"]
        if search_filter["softVersion"] != "": condition_dict["softversion="] = search_filter["softVersion"]
        if search_filter["problemDescription"] != "": condition_dict["problem LIKE"] = "%"+search_filter["problemDescription"]+"%"

        db =mysql_base.Db()
        total_work_record_amount = db.select(["count(fid)"], "workrecords_2023", condition_dict, "")
        return total_work_record_amount

def add_work_record(work_record_id, work_record_data):
    if work_record_data["registerDate"] >= "2024-01-01":
        print(f"aaaa{work_record_data}")

        # 对问题归属，问题分类等进行编码
        if work_record_data["problemAttribution"] != "":
            work_record_data["problemAttribution"] = data_dict_service.encode_data_item(work_record_data["problemAttribution"],constant.data_dict_code_map["error_attribution"])

        if work_record_data["problemType"] != "":
            problem_type = work_record_data["problemType"].rsplit("-", 1)
            work_record_data["problemType"] = data_dict_service.encode_data_item(problem_type[0], constant.data_dict_code_map["error_type"])
            work_record_data["problemFactor"] = data_dict_service.encode_data_item(problem_type[1], constant.data_dict_code_map["error_type_factor"])
            print(problem_type[1])
            print(f"aaaabbb{work_record_data['problemFactor']}")

        print(f"bbbb{work_record_data}")

    fieldDict = {}
    fieldDict["fid"] = work_record_id

    # 进行别名的转换，转换成数据库里字段名
    for key, value in constant.work_record_col_alias_map.items():
        temp_value = work_record_data.get(value)
        fieldDict[key] = "" if temp_value is None else temp_value

    table_name = "workrecords_2024" if work_record_data["registerDate"] >= "2024-01-01" else "workrecords_2023"
    db = mysql_base.Db()
    error = db.insert_copy(table_name, fieldDict)
    print(f"field dict: {fieldDict}")
    print(f"error: {error}")
    if error != "": raise Exception()

def update_work_record(work_record_id, work_record_data):
    if work_record_data["registerDate"] >= "2024-01-01":
        print(f"aaaa{work_record_data}")
        # 对问题归属，问题分类等进行编码
        work_record_data["problemAttribution"] = data_dict_service.encode_data_item(work_record_data["problemAttribution"], constant.data_dict_code_map["error_attribution"])
        problem_type = work_record_data["problemType"].rsplit("-", 1)
        work_record_data["problemType"] = data_dict_service.encode_data_item(problem_type[0], constant.data_dict_code_map["error_type"])
        work_record_data["problemFactor"] = data_dict_service.encode_data_item(problem_type[1], constant.data_dict_code_map["error_type_factor"])
        print(f"bbbb{work_record_data}")

    fieldDict = {}

    # 进行别名的转换，转换成数据库里字段名
    for key, value in constant.work_record_col_alias_map.items():
        if value == "registerDate": continue
        temp_value = work_record_data.get(value)
        fieldDict[key] = "" if temp_value is None else temp_value

    table_name = "workrecords_2024" if work_record_data["registerDate"] >= "2024-01-01" else "workrecords_2023"
    db = mysql_base.Db()
    db.update(table_name, fieldDict, {"fid=": work_record_id})

def cat_all_work_record_table_cols_alias():
    """
    select * from table 的情况下， 因为不想直接查询出现列名， 给所有列名起个别名
    """
    cat_alias_str = ''
    for key, value in constant.work_record_col_alias_map.items():
        cat_alias_str += f'{key} as {value}, '
    return cat_alias_str[:-2]


