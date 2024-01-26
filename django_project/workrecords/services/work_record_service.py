from mydata import mysql_base
from workrecords.config import constant
from workrecords.services import data_dict_service
from workrecords.exception.service.MyInvalidInputException import MyInvalidInputException

def get_work_record_detail(search_filter, curr_page, curr_page_size):
    """
    获取搜索条件下的工单的详细信息，分页搜索
    """
    # 工单搜索条件
    db = mysql_base.Db()
    table_name = "workrecords_2024" if search_filter["beginData"] >= "2024-01-01" else "workrecords_2023"
    condition_dict = translate_search_filter(search_filter)

    results = db.select(cat_all_work_record_table_cols_alias(), table_name, condition_dict,
                        f" ORDER BY createtime limit {str((curr_page - 1) * curr_page_size)}, {curr_page_size}")

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
        table_name = "workrecords_2024" if search_filter["beginData"] >= "2024-01-01" else "workrecords_2023"
        condition_dict = translate_search_filter(search_filter)
        db =mysql_base.Db()
        total_work_record_amount = db.select(["count(fid)"], table_name, condition_dict, "")
        return total_work_record_amount

def add_work_record(work_record_id, work_record_data):
    if work_record_data["registerDate"] >= "2024-01-01":
        # 对问题归属，问题分类等进行编码
        if work_record_data["problemAttribution"] != "":
            work_record_data["problemAttribution"] = data_dict_service.encode_data_item(work_record_data["problemAttribution"],constant.data_dict_code_map["error_attribution"])
        if work_record_data["problemType"] != "":
            problem_type = str(data_dict_service.encode_data_item(work_record_data["problemType"], constant.data_dict_code_map["error_type"]))
            work_record_data["problemType"] = int(problem_type[0:-4])
            work_record_data["problemFactor"] = int("1"+ problem_type[-4:])

    fieldDict = {}
    fieldDict["fid"] = work_record_id

    # 进行别名的转换，转换成数据库里字段名
    for key, value in constant.work_record_col_alias_map.items():
        temp_value = work_record_data.get(value)
        fieldDict[key] = "" if temp_value is None else temp_value

    table_name = "workrecords_2024" if work_record_data["registerDate"] >= "2024-01-01" else "workrecords_2023"
    db = mysql_base.Db()
    db.insert_copy(table_name, fieldDict)

def update_work_record(work_record_id, work_record_data):
    if work_record_data["registerDate"] >= "2024-01-01":
        # 对问题归属，问题分类等进行编码
        if work_record_data["problemAttribution"] != "":
            work_record_data["problemAttribution"] = data_dict_service.encode_data_item(work_record_data["problemAttribution"], constant.data_dict_code_map["error_attribution"])
        if work_record_data["problemType"] != "":
            problem_type = str(data_dict_service.encode_data_item(work_record_data["problemType"], constant.data_dict_code_map["error_type"]))
            work_record_data["problemType"] = int(problem_type[0:-4])
            work_record_data["problemFactor"] = int("1" + problem_type[-4:])

    fieldDict = {}

    # 进行别名的转换，转换成数据库里字段名
    for key, value in constant.work_record_col_alias_map.items():
        if value == "registerDate": continue
        temp_value = work_record_data.get(value)
        fieldDict[key] = "" if temp_value is None else temp_value

    table_name = "workrecords_2024" if work_record_data["registerDate"] >= "2024-01-01" else "workrecords_2023"
    db = mysql_base.Db()
    db.update(table_name, fieldDict, {"fid=": work_record_id})

def delete_work_record(work_record_id, work_record_data):
    db = mysql_base.Db()
    table_name = "workrecords_2024" if work_record_data["registerDate"] >= "2024-01-01" else "workrecords_2023"
    db.delete(table_name, {"fid=": work_record_id})

def cat_all_work_record_table_cols_alias():
    """
    select * from table 的情况下， 因为不想直接查询出现列名， 给所有列名起个别名
    :return 返回 select 列名 as 别名,... 的所有列名的字符串数组。
    """
    cat_alias_list = []
    for key, value in constant.work_record_col_alias_map.items():
        cat_alias_list.append(f'{key} as {value} ')
    return cat_alias_list

def translate_search_filter(search_filter):
    """
    将前端页面工单的搜索筛选条件，转换成 sql 语句中的where条件,以字典形式传给dao层。
    :param search_filter 工单的筛选条件，类型为字典。
    :return condition_dict 转成可以形成sql语句的字典， 如 {"createtime>=","2024-01-02"}
    """
    # 工单搜索条件
    condition_dict = {
        "createtime>=": search_filter["beginData"],
        "createtime<=": search_filter["endData"]
    }
    if search_filter["isSolved"] != "": condition_dict["issolve="] = search_filter["isSolved"]
    if search_filter["errorFunction"] != "": condition_dict["errorfunction="] = search_filter["errorFunction"]
    if search_filter["softVersion"] != "": condition_dict["softversion="] = search_filter["softVersion"]
    if search_filter["problemDescription"] != "": condition_dict["problem LIKE"] = "%" + search_filter["problemDescription"] + "%"
    if search_filter["beginData"] >= "2024-01-01":
        # 对问题归属的查询进行编码
        if search_filter["problemParty"] != "" and search_filter["problemAttribution"] != "":
            # 如果两项都有，说明是完整的一个问题归属，直接进行encode
            problem_party_encoded = data_dict_service.encode_data_item(f"{search_filter['problemParty']}-{search_filter['problemAttribution']}",
                                                                           constant.data_dict_code_map["error_attribution"])
            if problem_party_encoded is None: raise MyInvalidInputException(status=400, msg=f"问题归属的 {search_filter['problemParty']}-{search_filter['problemAttribution']} 的值不存在!")
            condition_dict["belong="] = problem_party_encoded
        elif search_filter["problemParty"] != "":
            # 如果只有出错方，那么需要查询出出错方的编号然后进行一个范围的查询
            problem_party_encoded = data_dict_service.encode_data_item(f"{search_filter['problemParty']}", constant.data_dict_code_map["error_attribution"])
            if problem_party_encoded is None: raise MyInvalidInputException(status=400, msg=f"问题归属的 {search_filter['problemParty']} 的值不存在!")
            condition_dict["belong>="] = problem_party_encoded * 1000
            condition_dict["belong<="] = (problem_party_encoded + 1) * 1000
        elif search_filter["problemAttribution"] != "":
            # 如果只有出错步骤，搜索出所有包含该出错步骤的问题归属，以or的方式进行查询
            problem_attribution_encoded = data_dict_service.encode_single_item(f"{search_filter['problemAttribution']}", constant.data_dict_code_map["error_attribution"])
            if isinstance(problem_attribution_encoded, int):
                # 查出唯一值，那么就是定位到了这个问题归属
                condition_dict["belong="] = problem_attribution_encoded
            elif isinstance(problem_attribution_encoded, list):
                # 查出多个问题归属，进行遍历使用 or 进行拼接
                # 生成一串的or的拼接，因为是一串的 or 语句，要给前后加上 ( 和 )。
                # 效果为 ... and ( belong=xxx and 0=0 or belong = xxx and 1=1 or belong = xxx and 1=1) ... and
                condition_dict["(belong="] = problem_attribution_encoded[0]
                for i in range(1, len(problem_attribution_encoded)):
                    condition_dict[f"{i}={i} OR belong="] = problem_attribution_encoded[i]
                condition_dict["1"] = "1)"
            else:
                raise MyInvalidInputException(status=400, msg=f"问题归属的 {search_filter['problemAttribution']} 的值不存在!")

        # 对问题分类的查询进行编码
        if search_filter["errorType"] != "" and search_filter["errorTypeDetail"]!="":
            # 如果两项都有，说明是完整的一个问题分类，直接进行encode
            error_service_encoded = data_dict_service.encode_data_item(f"{search_filter['errorType']}-{search_filter['errorTypeDetail']}",
                                                                           constant.data_dict_code_map["error_type"])
            if error_service_encoded is None: raise MyInvalidInputException(status=400, msg=f"问题分类的 {search_filter['errorType']}-{search_filter['errorTypeDetail']} 的值不存在!")
            condition_dict["errortype="] = error_service_encoded
        elif search_filter["errorType"] != "":
            # 如果只有出错服务，那么需要查询出服务的编号然后进行一个范围的查询
            error_service_encoded = data_dict_service.encode_data_item(f"{search_filter['errorType']}", constant.data_dict_code_map["error_type"])
            if error_service_encoded is None: raise MyInvalidInputException(status=400, msg=f"问题分类的 {search_filter['errorType']} 的值不存在!")
            condition_dict["errorType>="] = error_service_encoded * 1000
            condition_dict["errorType<="] = (error_service_encoded + 1) * 1000
        elif search_filter["errorTypeDetail"] != "":
            # 如果只有出错服务，搜索出所有包含该出错服务的问题分类，以or的方式进行查询
            error_service_encoded = data_dict_service.encode_single_item(f"{search_filter['errorTypeDetail']}",
                                                                               constant.data_dict_code_map["error_type"])
            if isinstance(error_service_encoded, int):
                # 查出唯一值，那么就是定位到了这个问题分类
                condition_dict["errorType="] = error_service_encoded
            elif isinstance(error_service_encoded, list):
                # 查出多个问题分类，进行遍历使用 or 进行拼接
                # 生成一串的or的拼接，因为是一串的 or 语句，要给前后加上 ( 和 )。
                # 效果为 ... and ( belong=xxx and 0=0 or belong = xxx and 1=1 or belong = xxx and 1=1) ... and
                condition_dict["(errorType="] = error_service_encoded[0]
                for i in range(1, len(error_service_encoded)):
                    condition_dict[f"{i}={i} OR errorType="] = error_service_encoded[i]
                condition_dict["1"] = "1)"
            else:
                raise MyInvalidInputException(status=400, msg=f"问题分类的 {search_filter['errorTypeDetail']} 的值不存在!")
        if search_filter["errorFactor"] != "":
            error_factor_encoded = data_dict_service.encode_single_item( search_filter["errorFactor"], constant.data_dict_code_map["error_type_factor"])

            if isinstance(error_factor_encoded, int):
                # 查出唯一值，那么就是定位到了这个问题分类
                condition_dict["errortypefactor="] = error_factor_encoded
            elif isinstance(error_factor_encoded, list):
                # 查出多个问题分类，进行遍历使用 or 进行拼接
                # 生成一串的or的拼接，因为是一串的 or 语句，要给前后加上 ( 和 )。
                # 效果为 ... and ( errortypefactor=xxx and 0=0 or errortypefactor = xxx and 1=1 or errortypefactor = xxx and 1=1) ... and
                condition_dict["(errortypefactor="] = error_factor_encoded[0]
                for i in range(1, len(error_factor_encoded)):
                    condition_dict[f"{i}={i} OR errortypefactor="] = error_factor_encoded[i]
                condition_dict["1"] = "1)"
            else:
                raise MyInvalidInputException(status=400, msg=f"问题分类的 {search_filter['errorFactor']} 的值不存在!")
    else:
        if search_filter["errorTypeOld"] != "": condition_dict["errortype="] = search_filter["errorTypeOld"]
    return condition_dict



def get_work_record_single_column_summary(begin_date, end_date, col_name, db=None, conditions=None, x_alias="x", y_alias="y"):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date,
    }
    if conditions is not None: condition_dict.update(conditions)
    saas_version_data = db.select([f"{col_name} as {x_alias}", f"count(*) as {y_alias}"], table_name, condition_dict, f" group by {x_alias} ")
    return saas_version_data

def get_work_record_distinct_version(begin_date, end_date, db=None, conditions=None, x_alias="x"):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date,
    }
    if conditions is not None: condition_dict.update(conditions)
    saas_version_data = db.select(["DISTINCT softversion as x"], table_name, condition_dict, " ORDER BY softversion ")
    return saas_version_data



def get_db(db):
    if db is None:
        db = mysql_base.Db()
    return db