import copy

def insert_version_into_list(list, label_key, label_value, version_list, version, amount, summary_row_label="合计"):
    """
    当需要数据结构为 [ {错误标签: 错误1, 版本号1: 错误数量, 版本号2: 错误数量, ... , 合计: 合计错误数量}, {...}, {...} ]
    想往里面插入一个错误的版本号的错误数量信息。
    :param list: 错误列表, 里面的元素是字典
    :param label_key: 错误标签，代表这个错误列表是关于什么错误的
    :param label_value: 错误标签的值，代表这个错误列表里的某个元素字典里面存放的数据是关于什么错误的
    :param version_list: 版本号的列表
    :param version: 需要插入的那个错误的版本号
    :param amount: 需要插入的那个错误的版本号的错误数量
    :param summary_row_label: 合计栏的标签，默认为"合计"
    """
    error_item_index = None
    for index, item in enumerate(list):
        # 如果这个错误已经在这个错误列表中登记过，返回这个错误所在的字典元素的位置
        if label_key in item and item[label_key] == label_value:
            error_item_index = index
    if error_item_index is None:
        # 放入该问题标签(如问题分类)和问题名字(如实施配置,异常数据处理等)，然后放入所有的查询结果的version
        new_error_factor_col1_dict = {label_key: label_value}
        new_error_factor_col1_dict.update({v: 0 for v in version_list})
        new_error_factor_col1_dict[summary_row_label] = amount
        new_error_factor_col1_dict[version] = amount
        list.append(new_error_factor_col1_dict)
    else:
        # 往版本字典添加更新错误数量
        list[error_item_index][version] += amount
        list[error_item_index][summary_row_label] += amount


def generate_analysis_table_data(function_list, error_factor_list, error_function_result, error_factor_result):
    """
    当需要生成表格为：表头是出错功能与问题因素，表尾是每一列出错功能/问题因素的合计，每一行的数据为某个版本的受理次数。
    （现在用于行业工单受理数据分析页面与电子票夹受理数据分析页面的受理问题表）
    @param function_list: 出错功能列表
    @param error_factor_list: 问题因素列表
    @param error_function_result: 筛选时间范围内出现的出错功能的每个版本的受理数
    @param error_factor_result: 筛选时间范围内出现的问题因素的每个版本的受理数
    """
    result = []
    row_template = {"程序版本": "合计", "受理合计": 0}
    row_template.update({key["name"]: 0 for key in function_list})
    row_template.update({key["name"]: 0 for key in error_factor_list})

    if len(error_function_result) == 0:
        result.append(row_template)
    else:
        row = copy.deepcopy(row_template)
        sum_row = copy.deepcopy(row_template)
        for i in range(len(error_function_result)):
            if row["程序版本"] != error_function_result[i]["softversion"]:
                if i != 0:
                    # 到了不同版本了,添加产品bug等错误因素信息添加，存入数据 result，新开一行
                    error_factor_row = next(item for item in error_factor_result if item.get("softversion") == row["程序版本"])
                    for key in error_factor_list:
                        row.update({key["name"]: error_factor_row[key["name"]]})
                        sum_row.update({key["name"]: sum_row[key["name"]] + error_factor_row[key["name"]]})
                    result.append(row)
                    row = copy.deepcopy(row_template)
                row["程序版本"] = error_function_result[i]["softversion"]
            # 进行对应的版本errorfunction数量添加和合计累计
            row[error_function_result[i]["errorfunction"]] += error_function_result[i]["amount"]
            row["受理合计"] += error_function_result[i]["amount"]
            sum_row[error_function_result[i]["errorfunction"]] += error_function_result[i]["amount"]
            sum_row["受理合计"] += error_function_result[i]["amount"]
        # 最后一行，因为循环到结尾，没有添加，这里添加最后一行version, 然后添加上合计栏
        error_factor_row = next(item for item in error_factor_result if item.get("softversion") == row["程序版本"])
        for key in error_factor_list:
            row.update({key["name"]: error_factor_row[key["name"]]})
            sum_row.update({key["name"]: sum_row[key["name"]] + error_factor_row[key["name"]]})
        result.append(row)
        result.append(sum_row)
    return result