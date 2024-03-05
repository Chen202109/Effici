from mydata import mysql_base
from workrecords.services.data_dict_service import get_error_function_dict_records, encode_data_item, decode_data_item
from workrecords.config import constant
from workrecords.utils.generate_table_utils import insert_version_into_list, generate_analysis_table_data

def get_ticket_folder_report_error_function_count(begin_date, end_date, db=None):
    db = get_db(db)

    # 获取票夹侧的出错功能的名称
    function_list = get_error_function_dict_records(["name"], 2, db)

    condition_dict = {
        "dictCode=": constant.data_dict_code_map["error_type_factor"],
        "level=": 1
    }
    error_factor_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

    # 开始查询生成出错功能和版本对比的表格数据
    sql = f'select softversion, errorfunction, count(*) as amount ' \
          f'FROM workrecords_2024 ' \
          f'WHERE createtime>="{begin_date}" AND createtime<="{end_date}" ' \
          f'AND promark="电子票夹" ' \
          f'GROUP BY softversion, errorfunction'
    error_function_result = db.select_offset(1, 1000, sql)

    # 开始查询问题因素和版本的数据
    sql = f'select softversion, ' \
          f'count(case when errortypefactor between 10100 and 10200 then 1 else NULL end ) as 产品bug, ' \
          f'count(case when errortypefactor between 10200 and 10300 then 1 else NULL end ) as 异常数据处理, ' \
          f'count(case when errortypefactor between 10300 and 10400 then 1 else NULL end ) as 实施配置, ' \
          f'count(case when errortypefactor between 10400 and 10500 then 1 else NULL end ) as 需求, ' \
          f'count(case when errortypefactor between 10500 and 10600 then 1 else NULL end ) as 其他 ' \
          f'FROM workrecords_2024 ' \
          f'WHERE createtime>="{begin_date}" AND createtime<="{end_date}" ' \
          f'AND promark="电子票夹" ' \
          f'GROUP BY softversion'
    error_factor_result = db.select_offset(1, 1000, sql)

    return generate_analysis_table_data(function_list, error_factor_list, error_function_result, error_factor_result)

def get_ticket_folder_report_problem_type_in_versions(begin_date, end_date, db=None):
    db = mysql_base.Db()
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date,
        "promark=": "电子票夹",
    }
    result = db.select(["errortypefactor", "softversion", "count(*) as amount"], "workrecords_2024", condition_dict,
                       "GROUP BY errortypefactor, softversion")
    version_list = sorted(set(item["softversion"].replace(".", "_") for item in result))

    # 要处理成这样的类型给前端渲染 [{"问题因素": "产品bug", "V4_3_2_1":3},{"问题因素": "实施配置", }]
    error_factor_col1_table = []
    error_factor_col2_table = []
    data = [{"problem": "问题因素", "problemData": error_factor_col1_table}, {"problem": "问题因素(细)", "problemData": error_factor_col2_table}]

    for item in result:
        error_factor = decode_data_item(item["errortypefactor"], constant.data_dict_code_map["error_type_factor"]).split("-")
        error_factor_col1 = error_factor[0]
        error_factor_col2 = error_factor[1]
        version = item["softversion"].replace(".", "_")
        amount = item["amount"]

        # 去找是否有登记过这个因素
        error_factor_col1_label = "问题因素"
        error_factor_col2_label = "问题因素(细)"
        insert_version_into_list(error_factor_col1_table, error_factor_col1_label, error_factor_col1, version_list, version, amount, "合计")
        insert_version_into_list(error_factor_col2_table, error_factor_col2_label, error_factor_col2, version_list, version, amount, "合计")

    return data

def get_ticket_folder_report_problem_type_in_function_version(begin_date, end_date, db=None):
    db = get_db(db)

    data = []

    # 获取票夹侧的出错功能的名称
    error_function_list = get_error_function_dict_records(["name"], 2, db)

    condition_dict = {
        # error_type_factor 005代表的是问题因素的那个数据字典
        "dictCode=": constant.data_dict_code_map["error_type_factor"],
        "level=": 1
    }
    error_factor_list = db.select(["code, name"], "work_record_data_dict", condition_dict, "")

    for error_factor_col1 in error_factor_list:
        # 将版本号里的"."转换成"_"，因为前端el-table的表头里如果字符串是带点的话会消失
        sql = f'SELECT replace(softversion,".","_") as softversion'
        for function in error_function_list:
            sql += f', SUM(IF(`errorfunction`="{function["name"]}",amount,0)) AS {function["name"]} '
        sql += ' FROM '
        sql += ' (SELECT softversion , errorfunction, errortypefactor, count(*) as amount '
        sql += ' FROM workrecords_2024 '
        sql += f' WHERE createtime>="{begin_date}" AND createtime<="{end_date}" '
        sql += f' AND promark="电子票夹" '
        sql += f' AND errortypefactor >= {error_factor_col1["code"] * 100} AND errortypefactor <= {(error_factor_col1["code"] + 1) * 100}'
        sql += ' GROUP BY softversion, errorfunction, errortypefactor ) A '
        sql += ' GROUP BY softversion '
        result = db.select_offset(1, 2000, sql)

        # 查询出来的结果像是[{'softversion': 'V4_3_1_3', '开票功能': Decimal('0'), '收缴业务': Decimal('0'), ...}, {...}]
        # 进行行列翻转
        saas_problem_type_and_function_data_in_version = []
        for function in error_function_list:
            new_item = {error_factor_col1["name"]: function["name"]}
            total = 0
            for item in result:
                new_item[item["softversion"]] = int(item[function["name"]])
                total += int(item[function["name"]])
            new_item["合计"] = total
            saas_problem_type_and_function_data_in_version.append(new_item)

        data.append({"problem": error_factor_col1["name"], "problemData": saas_problem_type_and_function_data_in_version})

    return data

def get_ticket_folder_report_problem_type_detail_in_versions(begin_date, end_date, db=None):
    db = get_db(db)
    data = []

    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date,
        "promark=": "电子票夹"
    }
    result = db.select(["errortypefactor", "softversion", "errortype", "count(*) as amount"], "workrecords_2024", condition_dict,
                       "GROUP BY errortypefactor, softversion, errortype")
    version_list = sorted(set(item["softversion"].replace(".", "_") for item in result))

    # 转化成前端可以直接渲染上el-table的形式,格式像这样
    # [{'异常数据处理': '报表功能', 'V3': 1, 'V4_3_1_2': 0, 'V4_3_1_3': 0, 'V4_3_2_0': 2, 'V4_3_2_1': 0}, {...}]
    error_factor_col1_list = {}
    for item in result:
        # 获取errorfactor大类的decode，如产品bug，实施配置等， errorfactor的码去掉后面两位的小类的编码所以除以100
        error_factor_col1_decoded = decode_data_item(int(item["errortypefactor"] / 100), constant.data_dict_code_map["error_type_factor"])
        error_type_decoded = decode_data_item(item["errortype"], constant.data_dict_code_map["error_type"])
        # 因为前端的el-table的表头如果字符串带'.'会失效，转换成"_"传给前端
        version = item["softversion"].replace(".", "_")
        amount = item["amount"]

        # 如果data里面还没有这一项errorfactor大类，添加这一个项目的字典，并且记录下这个在data中的index
        if error_factor_col1_list.get(error_factor_col1_decoded) is None:
            error_factor_col1_list[error_factor_col1_decoded] = len(data)
            data.append({ "problem": error_factor_col1_decoded, "problemData": []})

        # 从data中找到这一项errorfactor大类对应的问题分类的列表
        problem_data = data[error_factor_col1_list[error_factor_col1_decoded]]["problemData"]
        problem_data_func_label = error_factor_col1_decoded
        insert_version_into_list(problem_data, problem_data_func_label, error_type_decoded, version_list, version, amount, "合计")

    return data


def get_db(db):
    if db is None:
        db = mysql_base.Db()
    return db