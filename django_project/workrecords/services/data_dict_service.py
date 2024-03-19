from workrecords.exception.service.MyInvalidInputException import MyInvalidInputException
from mydata import mysql_base
import datetime

from workrecords.utils.type_casting_utils import cast_int_to_string
from workrecords.config import constant

table_name = "work_record_data_dict"

def add_data_dict(dict_name, db=None):
    """
    添加一个新的数据字典。如果指定dictCode并且合法的话,按照指定的dictCode来，否则自增。
    :param dict_name 新数据字典名称
    :param db 数据库连接
    """
    db = get_db(db)

    # 查看当前已有几个数据字典，编号已经到了多少，那新增字典的编号就是这个数量+1
    current_amount = get_data_dict_amount(db)
    dict_code = cast_int_to_string(current_amount + 1,3)

    # 新增数据字典，level为0， fid和dictCode一致
    fields = {
        "fid": dict_code,
        "dictCode" : dict_code,
        "code" : 1,
        "level" : 0,
        "parentCode" : None,
        "name" : dict_name,
        "enableTime" : str(datetime.date.today()),
        "enable" : 1,
        "childrenLength" : 0
    }

    try:
        # 往数据库新增数据字典，并将根节点的子节点数量+1
        db.insert_copy(table_name, fields)
        db.update(table_name, {"childrenLength" : current_amount+1}, {"level=" : -1})
    except Exception as e:
        print(f"添加数据字典出错，报错为: {str(e)}")

    return {"dictCode" : dict_code, "name": dict_name}

def add_data_dict_record(add_data_dict_form, db=None):
    """
    新增数据字典条目，若该条目已有，则不会有变动，不会抛出异常。
    :param add_data_dict_form 新增条目信息
    :param db 数据库连接
    """
    db = get_db(db)
    if add_data_dict_form["fullLabel"] != "":
        add_data_dict_record_by_full_label(add_data_dict_form["dictCode"], add_data_dict_form["fullLabel"], add_data_dict_form["systemLabel"], db)
    else:
        parent_node = None if add_data_dict_form["parentCode"]=="" else add_data_dict_form["parentCode"]
        add_data_dict_record_by_node(add_data_dict_form["dictCode"], int(add_data_dict_form["level"]), parent_node, add_data_dict_form["name"], add_data_dict_form["systemLabel"], db)
    return

def add_data_dict_record_by_full_label(dict_code, label, system_label, db):
    """
    通过完整标签如 基础信息-开票点管理-程序bug 来添加字典项目
    :param dict_code: 该数据字典的代码
    :param label: 完整的数据字典层级标签
    :param system_label 系统标识，1为行业2为票夹
    :param db: 和数据库的连接
    """
    data_dict_records = label.split("-")
    parent_code = None
    # 将完整标签拆分为一个个节点，以节点方式进行新增
    for i in range(len(data_dict_records)):
        code = add_data_dict_record_by_node(dict_code, i+1, parent_code, data_dict_records[i], system_label, db)
        parent_code = code
    return parent_code

def add_data_dict_record_by_node(dict_code, level, parent_code, name, system_label, db):
    """
    通过层级信息，上级层级编码 来添加字典项目
    :param dict_code: 该数据字典的代码
    :param level: 节点所在层级
    :param parent_code: 节点父级节点的编码
    :param name: 新增节点名
    :param system_label 系统标识，1为行业2为票夹
    :param db: 和数据库的连接
    """
    # 先尝试查找，看看是否已经存在这一项
    condition_dict = {
        "dictCode=": dict_code,
        "level=": level,
        "parentCode=": parent_code,
        "name=": name
    }
    result = db.select(["code", "enable", "childrenLength"], table_name, condition_dict, "")

    if isinstance(result, tuple):
        # 没有找到这一项, 先查看parentCode是否属实，不valid的parentCode要返回报错
        parent_result = db.select(["*"], table_name, {"dictCode=": dict_code, "level=": level - 1, "code=": parent_code, "enable=": 1}, "")
        if isinstance(parent_result, tuple):
            raise MyInvalidInputException(status=400, msg=f"输入的父节点编码 {parent_code} 的值不存在!")

        # valid就将这一条进行添加
        fields = {
            "dictCode": dict_code,
            "level": level,
            "parentCode": parent_code,
            "name": name,
            "enableTime": str(datetime.date.today()),
            "enable": 1,
            "childrenLength": 0
        }

        # 如果是出错功能字典，添加系统标签的值,此值暂且只在出错功能字典有意义。
        if dict_code==constant.data_dict_code_map["error_function"]:
            fields["systemLabel"] = system_label

        # 生成code, 通过父级节点的childrenLength来知道已经有了多少个节点，所以正常的话编号从这个的length+1
        new_code =  determine_code_dict.get(dict_code)(level, parent_result[0]["childrenLength"]+1, name, db)
        fields["code"] = int(str(fields["parentCode"]) + str(new_code)) if fields["parentCode"] is not None else int("1"+str(new_code))
        fields["fid"] = str(fields["dictCode"]) + str(fields["code"])
        try:
            db.insert_copy(table_name, fields)
            db.update(table_name, {"childrenLength": parent_result[0]["childrenLength"] + 1}, {"dictCode=": dict_code, "level=": level - 1, "code=": parent_code, "enable=": 1})
            return fields["code"]
        except Exception as e:
            print(f"添加数据字典出错，报错为: {str(e)}")
            raise Exception(f"添加数据字典出错，报错为: {str(e)}")
    else:
        # 找到了这一项，查看enable，是否开启，如果没开启把它开启
        if result[0]["enable"] == 0:
            db.update(table_name, { "enableTime" : str(datetime.date.today()), "enable" : 1, "disableTime" : None }, condition_dict)
        return result[0]["code"]

def determine_problem_attribution_code(level, sibling_length, name, db):
    """
    生成问题归属的编码
    :param level 层级
    :param sibling_length 父级节点已有多少子节点
    """
    if level == 1:
        return cast_int_to_string(sibling_length, 2)
    elif level == 2:
        return cast_int_to_string(sibling_length, 3)

def determine_problem_type_code(level, sibling_length, name, db):
    """
    生成问题分类的编码,第一层级编码长度为2，第二层级编码长度为3，第三层级编码通过005字典确认
    :param level 层级
    :param sibling_length 父级节点已有多少子节点
    :param name 如果是第三层级，代表问题因素的名称
    :param db 数据库连接
    """
    if level == 1:
        return cast_int_to_string(sibling_length, 2)
    elif level == 2:
        return cast_int_to_string(sibling_length, 3)
    elif level == 3:
        # 因为问题分类的最后一项是问题因素，是和数据字典005的第2层级的字典项关联在一起的，所以是需要去查005对应的问题因素的code来拼接上
        result = db.select(["code"], table_name, {"dictCode=": "005", "level=": 2, "name=": name, "enable=": 1}, "")
        if isinstance(result, tuple):
            # 没有找到，说明没有这个问题因素，报错，希望用户先去数据字典005插入该问题因素
            raise MyInvalidInputException(status=400, msg=f"输入的问题分类的问题因素 {name} 的值不存在! 请先去数据字典005添加该问题因素!")
        else:
            # 获取code的最后四位
            return cast_int_to_string(result, 4)

def determine_product_type_code(level, sibling_length, name, db):
    """
    生成产品类型的编码
    :param level 层级
    :param sibling_length 父级节点已有多少子节点
    """
    if level == 1:
        return cast_int_to_string(sibling_length, 2)

def determine_problem_function_code(level, sibling_length, name, db):
    """
    生成出错功能的编码
    :param level 层级
    :param sibling_length 父级节点已有多少子节点
    """
    if level == 1:
        return cast_int_to_string(sibling_length, 2)

def determine_problem_factor_code(level, sibling_length, name, db):
    """
    生成问题因素的编码, 第一层级编码长度为2，第二层级编码长度为2
    :param level 层级
    :param sibling_length 父级节点已有多少子节点
    """
    if level == 1:
        return cast_int_to_string(sibling_length, 2)
    elif level == 2:
        return cast_int_to_string(sibling_length, 2)

determine_code_dict = {
    "001": determine_problem_attribution_code,
    "002": determine_problem_type_code,
    "003": determine_product_type_code,
    "004": determine_problem_function_code,
    "005": determine_problem_factor_code,
}

def encode_data_item(item, dict_code):
    """
    将传入的数据字典条目在指定的数据字典查询编码， 查询成功返回编码。
    :param item 数据字典条目完整标签
    :param dict_code 所在数据字典的编码
    """
    item_cols = item.split("-")
    db =mysql_base.Db()
    # 因为第一层是null 
    parent_code = None
    for i in range(len(item_cols)):
        condition_dict = {
            "dictCode=": dict_code,
            "level=": i + 1,
            "name=": item_cols[i],
            "parentCode=": parent_code
        }
        parent_code = db.select(["code"], table_name, condition_dict, "")
        if isinstance(parent_code, tuple):
            return None
    return parent_code


def decode_data_item(item_code, dict_code):
    """
    传入条目编码, 查询对应的路径
    :param item_code 条目编码
    :param dict_code 所在数据字典编码
    """
    item = ""
    db =mysql_base.Db()
    parent_code = item_code
    while parent_code is not None:
        condition_dict = {"dictCode=": dict_code, "code=": parent_code}
        node = db.select(["name", "parentCode"], table_name, condition_dict, "")
        print(f"node is {node}")
        if isinstance(node, tuple):
            return None
        item = node[0]['name'] +"-" + item
        parent_code = node[0]["parentCode"]
    return item[:-1]


def encode_single_item(item, dict_code):
    """
    对一个不知层级关系只有名字的条目进行查询，如果有重复的条目，返回list, 如果是单个，返回list里面只有一个元素，如果没有查询到，返回None
    :param item 一个不知层级关系只有名字的条目, 如单位断电（这个是在问题归属的第二层，当不知道第一层是行业的时候，使用该方法进行查询）
    :param dict_code 所属的数据字典的编码
    """
    db = mysql_base.Db()
    condition_dict = {
        "dictCode=": dict_code,
        "name=": item,
    }
    result = db.select(["code"], table_name, condition_dict, "")
    return None if isinstance(result, tuple) else result


def get_data_dict_by_code(dict_code):
    """
    查询某个数据字典的所有条目
    :param dict_code 数据字典编号
    """
    db =mysql_base.Db()
    condition_dict = {"dictCode=": dict_code, "level!=":0}
    data_dict_old = db.select(["*"], table_name, condition_dict, "")
    return data_dict_old

def get_all_data_dict(db=None):
    """
    查询所有数据字典信息
    :return 一个包含了数据字典的dictCode 和 name 的列表
    """
    db = get_db(db)
    condition_dict = { "level=": 0}
    data_dict_list = db.select(["dictCode", "name"], table_name, condition_dict, " ORDER BY dictCode")
    return data_dict_list

def get_data_dict_amount(db=None):
    """
    :return 现在有多少个数据字典
    """
    db = get_db(db)
    condition_dict = {"level=": -1}
    amount = db.select(["childrenLength"], table_name, condition_dict, "")
    return amount

def get_data_dict_record_full_label_for_work_record(db=None):
    """
    获取以层级字典的数据格式的工单所需要的数据字典信息。
    工单需要产品类型，问题归属，问题分类，与出错功能的字典信息。
    """
    db=get_db(db)

    data = {}

    # 查询所有问题归属, 然后以 { party1: [xxx, xxx], party2:[xxx, xxx]}这样方式传给前端
    condition_dict = {
        # error_attribution 001代表的是问题归属的那个数据字典
        "t1.dictCode=": constant.data_dict_code_map["error_attribution"],
        "t2.dictCode=": constant.data_dict_code_map["error_attribution"],
        "t1.level=": 1,
        "t2.level=": 2,
    }
    problem_attribution_list = db.select([" t1.name as level1_name ", " t2.name as level2_name "],
                                         "work_record_data_dict t1 JOIN work_record_data_dict t2 ON t1.code = t2.parentCode",
                                         condition_dict, "")
    data["problemAttributionOptions"] = {}
    for item in problem_attribution_list:
        if data["problemAttributionOptions"].get(item["level1_name"]) is None:
            data["problemAttributionOptions"][item["level1_name"]] = []
        data["problemAttributionOptions"][item["level1_name"]].append(item["level2_name"])

    # 查询所有的问题分类
    condition_dict = {
        # error_type 002代表的是问题归属的那个数据字典
        "t1.dictCode=": constant.data_dict_code_map["error_type"],
        "t2.dictCode=": constant.data_dict_code_map["error_type"],
        "t1.level=": 1,
        "t2.level=": 2,
    }
    error_type_list = db.select([" t1.name as level1_name ", " t2.name as level2_name "],
                                "work_record_data_dict t1 JOIN work_record_data_dict t2 ON t1.code = t2.parentCode",
                                condition_dict, "")
    data["errorTypeOptions"] = {}
    for item in error_type_list:
        if data["errorTypeOptions"].get(item["level1_name"]) is None:
            data["errorTypeOptions"][item["level1_name"]] = []
        data["errorTypeOptions"][item["level1_name"]].append(item["level2_name"])

    # 查询所有产品类型
    condition_dict = {
        # product_type 003代表的是产品类型的那个数据字典
        "dictCode=": constant.data_dict_code_map["product_type"],
        "level=": 1
    }
    product_type_list = db.select(["name"], "work_record_data_dict", condition_dict, "")
    data["productTypeOptions"] = [item["name"] for item in product_type_list]

    # 查询所有问题功能
    condition_dict = {
        # error_function是dict 004代表的是问题功能的那个数据字典
        "dictCode=": constant.data_dict_code_map["error_function"],
        "level=": 1
    }
    error_function_list = db.select(["name"], "work_record_data_dict", condition_dict, "")
    data["errorFunctionOptions"] = [item["name"] for item in error_function_list]

    # 查询所有问题因素
    condition_dict = {
        # error_type_factor 005代表的是问题因素的那个数据字典
        "dictCode=": constant.data_dict_code_map["error_type_factor"],
        "level=": 2
    }
    error_factor_list = db.select(["name"], "work_record_data_dict", condition_dict, "")
    data["errorFactorOptions"] = [item["name"] for item in error_factor_list]

    return data

def get_error_function_dict_records(cols, system_label, db=None):
    """
    获取出错功能字典的条目
    :param cols 字段
    :param system_label 是哪个平台的出错功能, 行业为1，票夹为2
    :param db 数据库连接
    """
    db=get_db(db)
    condition_dict = {
        # error_function是dict 004代表的是问题功能的那个数据字典
        "dictCode=": constant.data_dict_code_map["error_function"],
        "level=": 1,
        "systemLabel=": system_label
    }
    function_list = db.select(cols, "work_record_data_dict", condition_dict, "")
    return function_list


def get_db(db):
    if db is None:
        db = mysql_base.Db()
    return db