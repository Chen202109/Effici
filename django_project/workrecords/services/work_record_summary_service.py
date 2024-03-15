from datetime import datetime, timedelta
from mydata import mysql_base
from workrecords.config import constant
import pandas as pd

from workrecords.services.data_dict_service import encode_data_item, decode_data_item, get_error_function_dict_records
from workrecords.services.work_record_service import get_work_record_single_column_summary
from workrecords.utils.generate_table_utils import insert_version_into_list, generate_analysis_table_data


def get_work_record_month_summary(begin_date, end_date, system_label=None):
    """
    查询传入的时间范围内每个月的受理数量，并且归纳那个月出错功能的前五
    :param begin_date 查询起始时间
    :param end_date 查询截止时间
    :param system_label 标识是哪个系统的工单受理问题，None代表都查询，1代表行业，2代表票夹
    """
    promark_condition_sql = ''
    if system_label == "1":
        promark_condition_sql = 'AND ( promark="V3标准产品" OR promark="V4标准产品" OR promark="增值产品")'
    elif system_label=="2":
        promark_condition_sql=  'AND promark="电子票夹"'

    print(f"received sql: {promark_condition_sql}")

    db = mysql_base.Db()
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    sql = f' SELECT MONTH(createtime) AS Month, errorfunction, COUNT(*) AS ProblemAmount ' \
          f' FROM {table_name} ' \
          f' WHERE MONTH(createtime) between {datetime.strptime(begin_date, "%Y-%m-%d").month} AND {datetime.strptime(end_date, "%Y-%m-%d").month} ' \
          f' {promark_condition_sql} '\
          f' GROUP BY MONTH(createtime), errorfunction'
    saas_month_data = db.select_offset(1, 2000, sql)

    # 因为前端想要tooltip展示每个月出错功能的前五，所以在这里进行每个月出错功能的排序
    series_data = []
    curr_month = 0
    month_amount = 0
    month_function_list = []
    for i in range(len(saas_month_data)):
        if curr_month != 0 and curr_month != saas_month_data[i]['Month']:
            # 说明要换成下个月的数据了，所以将当前存储的当前月份的数据进行出错功能的排序取前五和添加到series_data中
            month_function_list.sort(key=lambda x: x['amount'], reverse=True)
            series_data.append({'x': str(curr_month) + '月', 'y': month_amount, 'functionType': month_function_list[0:5]})
            # 将临时数据进行清空
            month_amount = 0
            month_function_list = []
        # 还在当前月份，那么就往临时数据里面添加当前月份的出错功能和累加出错的量
        curr_month = saas_month_data[i]['Month']
        month_amount += saas_month_data[i]['ProblemAmount']
        month_function_list.append({"function": saas_month_data[i]['errorfunction'], 'amount': saas_month_data[i]['ProblemAmount']})
    if len(month_function_list) != 0:
        # 已经到查询的月份的末尾了跳出了，但是最后一个月份的数据还未进行sort和加入seriesData之中，进行添加
        month_function_list.sort(key=lambda x: x['amount'], reverse=True)
        series_data.append({'x': str(curr_month) + '月', 'y': month_amount, 'functionType': month_function_list[0:5]})
    return series_data


def get_work_record_version_function_summary(begin_date, end_date, province, function_list):
    data = []

    db = mysql_base.Db()
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province != '全国': condition_dict["region="] = province
    saas_version_data = db.select(["DISTINCT softversion as x"], table_name, condition_dict, " ORDER BY softversion ")

    for function_item in function_list:
        condition_dict["errorfunction="] = function_item
        saas_function_data = db.select(["softversion as x", "COUNT(*) as y"], table_name, condition_dict, " GROUP BY softversion ")
        saas_version_data = [{'x': entry['x'], 'y': next((value['y'] for value in saas_function_data if value['x'] == entry['x']), 0)} for entry in
                             saas_version_data]
        data.append({'seriesName': function_item, 'seriesData': saas_version_data})
    return data


def get_work_record_province_function_summary(begin_date, end_date, function_list, system_label=None):
    """
    查询传入的时间范围内每个省份的受理量，并且统计每个省份的受理的所指定的出错功能。
    :param begin_date 查询起始时间
    :param end_date 查询截止时间
    :param function_list 所指定的出错功能，是列表形式，以,分割
    :param system_label 标识是哪个系统的工单受理问题，None代表都查询，1代表行业，2代表票夹
    """
    data = []
    db = mysql_base.Db()
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if system_label == "1":
        condition_dict["(promark='增值产品' OR promark='V3标准产品' OR promark='V4标准产品') AND 1="] = 1
    elif system_label == "2":
        condition_dict["promark="] = "电子票夹"
    region_list = db.select(["DISTINCT region as x"], table_name, condition_dict, "")

    # 对每个功能进行查找
    for function_item in function_list:
        condition_dict["errorfunction="] = function_item
        saas_function_data = db.select(["region as x", "count(*) as y"], table_name, condition_dict, " group by x")
        saas_province_data = [{'x': entry['x'], 'y': next((value['y'] for value in saas_function_data if value['x'] == entry['x']), 0)} for entry in
                              region_list]
        data.append({'seriesName': function_item, 'seriesData': saas_province_data})

    # 对省份按受理数量进行排序
    sorted_region = []
    y_max = 0
    xAxis = region_list

    # 统计省份对应的几个功能加起来的受理数量
    for item in xAxis:
        y_sum = 0
        for function_data in data:
            y = next(filter(lambda x: x['x'] == item['x'], function_data['seriesData']))['y']
            y_sum += y
            y_max = y if y > y_max else y_max
        sorted_region.append({'x': item['x'], 'y': y_sum})

    # 排序并取出省份的list
    sorted_region.sort(key=lambda x: x['y'], reverse=True)
    sorted_region_x = [item['x'] for item in sorted_region]

    # 根据排序好的省份，重新将数据根据顺序装填如每一个function的seriesData中
    for i in range(len(function_list)):
        data[i]['seriesData'] = [next(filter(lambda x: x['x'] == region, data[i]['seriesData'])) for region in sorted_region_x]

    # 加上yMax的值，该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
    return {"data": data, "yMax": y_max}


def get_work_record_product_type_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province != '全国': condition_dict["region="] = province
    saas_agency_type_data = db.select(["agentype as x", "count(*) as y"], table_name, condition_dict, " group by agentype ")
    return [{'seriesName': province + "受理行业种类", 'seriesData': saas_agency_type_data}]


def get_summary_item_amount(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
    real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    province_condition_sql = "" if province == "全国" else f' AND region = "{province}" '

    work_record_table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"

    # 对合计的数据进行统计添加
    sql = f'SELECT "受理问题合计" as x, count(*) as y from {work_record_table_name} WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'SELECT "V4 license受理合计" as x, count(*) from license_2023 WHERE authorizeddate >= "{begin_date}" AND authorizeddate <= "{end_date}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'select "私有化重大故障合计" as x, count(*) from majorrecords WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'select "生产监控问题合计" as x, count(*) from monitorrecords WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'select "增值服务开通合计" as x, count(*) from orderprodct_2023 WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" {province_condition_sql} '
    saas_country_summary_table_data = db.select_offset(1, 2000, sql)

    # 上线单位数量统计, 因为是跨越时间的查询，查询这段时间内的单位新增
    begin_time_year = int(begin_date.split("-")[0])
    begin_time_month = int(begin_date.split("-")[1])
    end_time_year = int(end_date.split("-")[0])
    end_time_month = int(end_date.split("-")[1])
    agency_amount = 0
    while begin_time_year <= end_time_year:
        # 打开该年的csv, 因为现在只有2020-2023,其他年份的会找不到报错
        try:
            dataframe = pd.read_csv(f"{constant.AGENCY_ACCOUNT_FILE_ROOT}agency_account_increment_{begin_time_year}.csv", sep=',', index_col=0)
        except FileNotFoundError:
            begin_time_year += 1
            continue
        if begin_time_year == end_time_year:
            # 找到相同年份了，那么就持续相加直到月份相同为止
            while True:
                agency_amount += int(dataframe.loc[province, str(begin_time_month) + '月'])
                if begin_time_month == end_time_month:
                    break
                begin_time_month += 1
            break
        else:
            # 还没到相同年份， 将这一年到年末的数据相加
            while begin_time_month <= 12:
                agency_amount += int(dataframe.loc[province, str(begin_time_month) + '月'])
                begin_time_month += 1
            begin_time_month = 1
            begin_time_year += 1
    # 对上线单位数量统计进行读取和插入到summary table中
    saas_country_summary_table_data.insert(0, {"x": '上线单位合计', "y": agency_amount})

    saas_country_summary_table = []
    saas_country_summary_table.append({'seriesName': province + "合计数据", 'seriesData': saas_country_summary_table_data})

    return saas_country_summary_table


def get_work_record_error_function_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province != '全国': condition_dict["region="] = province
    saas_function_type_data = db.select(["errorfunction as x", "count(*) as y"], table_name, condition_dict, " group by errorfunction ")
    return saas_function_type_data


def get_work_record_problem_type_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province != '全国': condition_dict["region="] = province
    if begin_date < "2024-01-01":
        saas_problem_type_data = db.select(["errorType as x", "count(*) as y"], table_name, condition_dict, " group by x ")
    else:
        # 因为2024年的模板中，产品bug,异常因素等被归为问题错误因素，是存在errortypefactor中的前三位数字来标识的
        saas_problem_type_data = db.select(["round(errortypefactor/100) as x", "count(*) as y"], table_name, condition_dict, " group by x ")
        # 对查出来的问题错误因素进行解码
        for item in saas_problem_type_data:
            item["x"] = decode_data_item(int(item["x"]), constant.data_dict_code_map["error_type_factor"])
    return saas_problem_type_data


def get_work_record_version_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province != '全国': condition_dict["region="] = province
    saas_soft_version_data = db.select(["softversion as x", "errorfunction", "count(*) as y"], table_name, condition_dict,
                                       " group by softversion, errorfunction ")

    # 因为前端想要tooltip展示每个版本号出错功能的前三，所以在这里进行每个版本出错功能的排序
    series_data = []
    curr_version = 0
    version_amount = 0
    version_function_list = []
    for i in range(len(saas_soft_version_data)):

        if curr_version != 0 and curr_version != saas_soft_version_data[i]['x']:
            # 说明要换成下个版本的数据了，所以将当前存储的当前版本的数据进行出错功能的排序取前三和添加到series_data中
            version_function_list.sort(key=lambda x: x['amount'], reverse=True)
            series_data.append({'x': curr_version, 'y': version_amount, 'functionType': version_function_list[0:3]})
            # 将临时数据进行清空
            version_amount = 0
            version_function_list = []

        # 还在当前版本，那么就往临时数据里面添加当前月份的出错功能和累加出错的量
        curr_version = saas_soft_version_data[i]['x']
        version_amount += saas_soft_version_data[i]['y']
        version_function_list.append({"function": saas_soft_version_data[i]['errorfunction'], 'amount': saas_soft_version_data[i]['y']})

        if i == len(saas_soft_version_data) - 1:
            # 说明所有数据查到最后一项了，该要退出循环了，将这个月份的数据加入series_data中
            version_function_list.sort(key=lambda x: x['amount'], reverse=True)
            series_data.append({'x': curr_version, 'y': version_amount, 'functionType': version_function_list[0:3]})
    return series_data


def get_work_record_province_summary(begin_date, end_date, db=None, region_alias="x", value_alias="y"):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    saas_province_problem_data = db.select([f"region as {region_alias}", f"count(*) as {value_alias}"], table_name, condition_dict,
                                           " group by region ")
    return saas_province_problem_data


def get_work_record_country_map_summary(saas_province_problem_data, saas_province_agency_account_data):
    # 生成关于全国省份的数据, 这里因为saas_province_problem_data和saas_province_agency_account_data查询的地区的顺序不一致，
    # 所以全部以constant.china_province_list顺序为基准往里面填数据
    saas_country_data = []
    # 用于visualMap使用，显示颜色渐变，给这个组件提供一个数据的最大值
    value_max = 0
    for prov in constant.china_province_list:
        value = next((item['value'] for item in saas_province_problem_data if item['name'] == prov), 0)
        value_max = value if value > value_max else value_max
        agency_value = next((item['value'] for item in saas_province_agency_account_data if item['name'] == prov), 0)
        #  数组格式为[{"name":"省份名称","value":受理问题的数量}] ， 因为echarts地图他使用的数据格式是name和value，所以得对应上不能自定义值
        saas_country_data.append({'name': prov, 'value': value, 'agencyValue': agency_value})
    data = { "data": [{'seriesName': "全国受理数量", 'seriesData': saas_country_data}], "valueMax":value_max}
    return data


def get_work_record_resource_pool_error_function_summary(begin_date, end_date, resource_pool, function_names, version_list, db=None):
    db = get_db(db)
    # 生成对受理问题查询时候省份条件的语句
    province_list = constant.source_pool_province_map[resource_pool]
    resource_pool_condition = '('
    for i in province_list:
        resource_pool_condition += f'region = "{i}" or '
    resource_pool_condition = resource_pool_condition[:-3] + ")"

    data = []

    # 对每个功能的受理问题进行统计
    for function_name in function_names:
        condition_dict = {
            "errorfunction=": function_name,
            "environment=": "公有云",
            "softversion!=": "V3",
            f"{resource_pool_condition} and 1=": "1"
        }
        saas_function_data = get_work_record_single_column_summary(begin_date, end_date, "softversion", conditions=condition_dict, db=db)
        series_data = [{'x': entry['x'], 'y': next((value['y'] for value in saas_function_data if value['x'] == entry['x']), 0)} for entry in version_list]
        data.append({'seriesName': function_name, 'seriesData': series_data})

    return data


def get_work_record_province_agency_summary():
    pass


def get_work_record_error_function_count_old(beginData, endData,db=None):

    analysisData={
        'tableData': []
    }

    db = get_db(db)

    # ■■■ 开始分页查询，获得对应时间范围内，【数据汇报】--->受理问题的表格数据
    # total是每个版本的受理数量合计，其他用了 列传行 的办法
    sql = f'SELECT COALESCE(softversion,0) as softversion,' \
          f'SUM(IF(`errorfunction`="报表功能",数量,0))+SUM(IF(`errorfunction`="开票功能",数量,0))' \
          f'+SUM(IF(`errorfunction`="license重置",数量,0))+SUM(IF(`errorfunction`="增值服务",数量,0))' \
          f'+SUM(IF(`errorfunction`="收缴业务",数量,0))+SUM(IF(`errorfunction`="通知交互",数量,0))' \
          f'+SUM(IF(`errorfunction`="核销功能",数量,0))+SUM(IF(`errorfunction`="票据管理",数量,0))' \
          f'+SUM(IF(`errorfunction`="安全漏洞",数量,0))+SUM(IF(`errorfunction`="打印功能",数量,0))' \
          f'+SUM(IF(`errorfunction`="数据同步",数量,0))+SUM(IF(`errorfunction`="反算功能",数量,0))' \
          f'+SUM(IF(`errorfunction`="单位开通",数量,0)) as total, ' \
          f'SUM(IF(`errorfunction`="报表功能",数量,0)) AS report, ' \
          f'SUM(IF(`errorfunction`="开票功能",数量,0)) AS openbill, ' \
          f'SUM(IF(`errorfunction`="license重置",数量,0)) AS licenseReset, ' \
          f'SUM(IF(`errorfunction`="增值服务",数量,0)) AS added, ' \
          f'SUM(IF(`errorfunction`="收缴业务",数量,0)) AS collection, ' \
          f'SUM(IF(`errorfunction`="通知交互",数量,0)) AS exchange, ' \
          f'SUM(IF(`errorfunction`="核销功能",数量,0)) AS writeoff, ' \
          f'SUM(IF(`errorfunction`="票据管理",数量,0)) AS billManagement, ' \
          f'SUM(IF(`errorfunction`="安全漏洞",数量,0)) AS security, ' \
          f'SUM(IF(`errorfunction`="打印功能",数量,0)) AS print, ' \
          f'SUM(IF(`errorfunction`="数据同步",数量,0)) AS datasync, ' \
          f'SUM(IF(`errorfunction`="反算功能",数量,0)) AS inverse, ' \
          f'SUM(IF(`errorfunction`="单位开通",数量,0)) AS opening, ' \
          f'SUM(IF(`errortype` = "产品BUG", 数量, 0)) AS softbug, ' \
          f'SUM(IF(`errortype` = "实施配置", 数量, 0)) AS sspz, ' \
          f'SUM(IF(`errortype` = "异常数据处理", 数量, 0)) AS ycsjcl ' \
          f'FROM' \
          f'(select softversion , errorfunction, errortype, count(*) as 数量 ' \
          f'from workrecords_2023 where createtime>="{beginData}" and createtime<="{endData}" ' \
          f'GROUP BY softversion, errorfunction, errortype ) A ' \
          f'GROUP BY softversion'
    tableData = db.select_offset(1, 1000, sql)

    func_list = ["softversion", "total", "report", "openbill", "licenseReset", "added", "collection", "exchange", "writeoff",
                 "billManagement", "security", "print", "datasync", "inverse", "opening", "softbug", "sspz", "ycsjcl"]

    # 当查询时间不对，数据库内没有那段时间的数据的时候，他会返回一个tuple而不是一个list，所以将他初始化成一个list
    tableData = [] if tableData == () else tableData

    # 【数据汇报】--->受理问题的柱形图
    # 将 tableData 查询的数据中，softversion的内容组装到一个数组中给前端myChart柱形图setOption传参
    # myChart_xAxis表示softversion版本号 和 myChart_series表示total合计数量
    myChart_xAxis = []
    myChart_series = []
    for i in range(len(tableData)):
        myChart_xAxis.append(tableData[i]['softversion'])  # 数组，前端myChart 组件的xAxis 中data数据
        myChart_series.append(tableData[i]['total'])  # 数组，前端myChart 组件的series 中data数据

    # 给tableData最后一行加上合计
    summary = {key: 0 for key in func_list}
    summary["softversion"] = "合计"
    for i in range(1, len(func_list)):
        summary[func_list[i]] = sum([item[func_list[i]] for item in tableData])
    tableData.append(summary)

    analysisData['tableData'] = tableData  # 添加数组元素 【数据汇报】--->受理问题的内容
    analysisData['myChart_xAxis'] = myChart_xAxis  # 添加数组元素 【数据汇报】--->受理问题的柱形图x轴数据
    analysisData['myChart_series'] = myChart_series  # 添加数组元素 【数据汇报】--->受理问题的柱形图中柱形上显示的数量

    # 【数据汇报】--->受理问题的饼状图
    # 将 tableData 查询的数据中，errorfunction 问题类型对应的数量，组装到一个数组中给前端annularChart饼形图setOption传参
    # annularChart_data 返回像 [{'value': 19, 'errorfunction': 'license重置'},{'value': 8, 'errorfunction': '单位开通'}]

    sql = f'select count(1) as value, errorfunction as name ' \
          f'from workrecords_2023 ' \
          f'where createtime>="{beginData}" and createtime<="{endData}" ' \
          f'GROUP BY errorfunction'
    annularChart_data = db.select_offset(1, 1000, sql)

    analysisData['annularChart_data'] = annularChart_data  # 添加数组元素 【数据汇报】---> 饼状图形数据
    # ■■■ 结束 受理问题 相关的数据获取

    return analysisData

def get_work_record_error_type_to_error_function_count_old(begin_date, end_date,db=None):

    data = []

    db = get_db(db)
    problem_type_list = ["产品bug", "实施配置", "异常数据处理"]

    for problem_type in problem_type_list:
        sql = f'SELECT softversion as softversion,' \
              f'SUM(IF(`errorfunction`="报表功能",数量,0)) AS 报表功能, ' \
              f'SUM(IF(`errorfunction`="开票功能",数量,0)) AS 开票功能, ' \
              f'SUM(IF(`errorfunction`="license重置",数量,0)) AS license重置, ' \
              f'SUM(IF(`errorfunction`="增值服务",数量,0)) AS 增值服务, ' \
              f'SUM(IF(`errorfunction`="收缴业务",数量,0)) AS 收缴业务, ' \
              f'SUM(IF(`errorfunction`="通知交互",数量,0)) AS 通知交互, ' \
              f'SUM(IF(`errorfunction`="核销功能",数量,0)) AS 核销功能, ' \
              f'SUM(IF(`errorfunction`="票据管理",数量,0)) AS 票据管理, ' \
              f'SUM(IF(`errorfunction`="安全漏洞",数量,0)) AS 安全漏洞, ' \
              f'SUM(IF(`errorfunction`="打印功能",数量,0)) AS 打印功能, ' \
              f'SUM(IF(`errorfunction`="数据同步",数量,0)) AS 数据同步, ' \
              f'SUM(IF(`errorfunction`="反算功能",数量,0)) AS 反算功能, ' \
              f'SUM(IF(`errorfunction`="单位开通",数量,0)) AS 单位开通 ' \
              f'FROM ' \
              f'(select softversion , errorfunction, errortype, count(*) as 数量 ' \
              f'from workrecords_2023 where createtime>="{begin_date}" and createtime<="{end_date}" and errortype = "{problem_type}" ' \
              f'GROUP BY softversion, errorfunction, errortype ) A ' \
              f'GROUP BY softversion'

        saas_problem_type_and_function_data = db.select_offset(1, 2000, sql)

        # 转化成前端可以直接渲染上el-table的形式,格式像这样
        # [{'异常数据处理': '报表功能', 'V3': 1, 'V4_3_1_2': 0, 'V4_3_1_3': 0, 'V4_3_2_0': 2, 'V4_3_2_1': 0},
        # {'异常数据处理': '开票功能', 'V3': 3, 'V4_3_1_2': 1, 'V4_3_1_3': 3, 'V4_3_2_0': 7, 'V4_3_2_1': 0},]
        saas_problem_type_and_function_data_in_version = []
        # 对每个功能生成一条这样的数据{'异常数据处理': '报表功能', 'V3': 1, 'V4_3_1_2': 0, 'V4_3_1_3': 0, 'V4_3_2_0': 2, 'V4_3_2_1': 0}
        for function_type in constant.work_record_error_function_list:
            new_item = {problem_type: function_type}
            total = 0
            for item in saas_problem_type_and_function_data:
                # 因为前端那边的el-table，如果是V4.3.2.0这样有带.的，他会没办法自动把数值放上去，所以这边为了前端的格式需要将之转化成V4_3_2_0
                new_item[item["softversion"].replace(".", "_")] = int(item[function_type])
                total += int(item[function_type])
            new_item["合计"] = total
            saas_problem_type_and_function_data_in_version.append(new_item)

        data.append({'problemType': problem_type, 'problemTypeData': saas_problem_type_and_function_data_in_version})

    return data

def get_work_record_report_error_function_count_new(begin_date, end_date, system_label=None, db=None):
    """
    查询2024年工单模板筛选时间范围内的工单关于问题分类的次数统计
    :param begin_date 查询起始时间
    :param end_date 查询截止时间
    :param system_label 标识是哪个系统的工单受理问题，None代表都查询，1代表行业，2代表票夹
    :param db 数据库连接
    """
    promark_condition_sql = ''
    if system_label == "1":
        promark_condition_sql = 'AND ( promark="V3标准产品" OR promark="V4标准产品" OR promark="增值产品")'
    elif system_label=="2":
        promark_condition_sql=  'AND promark="电子票夹"'

    db = get_db(db)

    # 获取行业侧的出错功能的名称
    function_list = get_error_function_dict_records(["name"], system_label, db)

    condition_dict = {
        # error_type_factor 005代表的是问题因素的那个数据字典
        "dictCode=": constant.data_dict_code_map["error_type_factor"],
        "level=": 1
    }
    error_factor_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

    # 开始查询生成出错功能和版本对比的表格数据
    sql = f'select softversion, errorfunction, count(*) as amount ' \
          f'FROM workrecords_2024 ' \
          f'WHERE createtime>="{begin_date}" AND createtime<="{end_date}" ' \
          f'{promark_condition_sql} ' \
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
          f'{promark_condition_sql} ' \
          f'GROUP BY softversion'
    error_factor_result = db.select_offset(1, 1000, sql)

    return generate_analysis_table_data(function_list, error_factor_list, error_function_result, error_factor_result)

def get_work_record_report_problem_type_in_versions_new(begin_date, end_date, party_selected, system_label=None, db=None):
    db = get_db(db)
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date,
    }
    if system_label == "1":
        condition_dict["(promark='增值产品' OR promark='V3标准产品' OR promark='V4标准产品') AND 1="] = 1
    elif system_label == "2":
        condition_dict["promark="] = "电子票夹"
    if party_selected != "全部":
        party_encoded = encode_data_item(party_selected, constant.data_dict_code_map["error_attribution"])
        # 10^3 是因为party的二级现在是3位数，所以是10^3
        condition_dict["belong>="] = party_encoded * 1000
        condition_dict["belong<"] = (party_encoded + 1) * 1000
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
        error_factor_col1_label = "问题因素" if party_selected == "全部" else f"{party_selected}-问题因素"
        error_factor_col2_label = "问题因素(细)" if party_selected == "全部" else f"{party_selected}-问题因素(细)"

        insert_version_into_list(error_factor_col1_table, error_factor_col1_label, error_factor_col1, version_list, version, amount, "合计数量")
        insert_version_into_list(error_factor_col2_table, error_factor_col2_label, error_factor_col2, version_list, version, amount)

    return data

def get_work_record_report_problem_type_detail_in_versions_new(begin_date, end_date, party_selected="全部", system_label=None, db=None):
    """

    """
    db = get_db(db)
    data = []

    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date,
    }
    if system_label == "1":
        condition_dict["(promark='增值产品' OR promark='V3标准产品' OR promark='V4标准产品') AND 1="] = 1
    elif system_label == "2":
        condition_dict["promark="] = "电子票夹"
    if party_selected != "全部":
        party_encoded = encode_data_item(party_selected, constant.data_dict_code_map["error_attribution"])
        # 10^3 是因为party的二级现在是3位数，所以是10^3
        condition_dict["belong>="] = party_encoded * 1000
        condition_dict["belong<"] = (party_encoded + 1) * 1000
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
            data.append({
                "problem": error_factor_col1_decoded,
                "problemData": []
            })

        # 从data中找到这一项errorfactor大类对应的问题分类的列表
        problem_data = data[error_factor_col1_list[error_factor_col1_decoded]]["problemData"]
        problem_data_func_label = error_factor_col1_decoded if party_selected == "全部" else f"{party_selected}-{error_factor_col1_decoded}"
        insert_version_into_list(problem_data, problem_data_func_label, error_type_decoded, version_list, version, amount, "合计")

    return data

def get_work_record_report_problem_type_in_function_version_view_new(begin_date, end_date, party_selected, system_label, db=None):
    promark_condition_sql = ''
    if system_label == "1":
        promark_condition_sql = 'AND ( promark="V3标准产品" OR promark="V4标准产品" OR promark="增值产品")'
    elif system_label=="2":
        promark_condition_sql=  'AND promark="电子票夹"'

    db = get_db(db)

    data = []

    # 获取行业侧的出错功能的名称
    error_function_list = get_error_function_dict_records(["name"], system_label, db)

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
        sql += f' {promark_condition_sql} '
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






# 暂时放放在这个service

def get_large_problem_province_summary(begin_date, end_date, db=None):
    db = get_db(db)
    table_name = "majorrecords"
    # 因为majorrecords表的时间为yyyy-MM-dd HH:mm:ss，所以会导致搜索结尾日期时候 "2024-01-01 01:00:00" > "2024-01-01"， 避免如此，将搜索时间范围结尾加一
    condition_dict = {
        "createtime>=": str(datetime.strptime(begin_date, '%Y-%m-%d')),
        "createtime<=": str(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
    }
    saas_large_problem_province_data = db.select(["region as x", "count(*) as y"], table_name, condition_dict, " group by region ")
    return saas_large_problem_province_data


def get_large_problem_type_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "majorrecords"
    # 因为majorrecords表的时间为yyyy-MM-dd HH:mm:ss，所以会导致搜索结尾日期时候 "2024-01-01 01:00:00" > "2024-01-01"， 避免如此，将搜索时间范围结尾加一
    condition_dict = {
        "createtime>=": str(datetime.strptime(begin_date, '%Y-%m-%d')),
        "createtime<=": str(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
    }
    if province != '全国': condition_dict["region="] = province
    saas_large_problem_type_data = db.select(["errorType as x", "count(*) as y"], table_name, condition_dict, " group by errorType ")
    return saas_large_problem_type_data


def get_monitor_problem_type_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "monitorrecords"
    # 因为monitorrecords表的时间为yyyy-MM-dd HH:mm:ss，所以会导致搜索结尾日期时候 "2024-01-01 01:00:00" > "2024-01-01"， 避免如此，将搜索时间范围结尾加一
    condition_dict = {
        "createtime>=": str(datetime.strptime(begin_date, '%Y-%m-%d')),
        "createtime<=": str(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
    }
    if province != '全国': condition_dict["region="] = province
    saas_large_problem_type_data = db.select(["errorType as x", "count(*) as y"], table_name, condition_dict, " group by errorType ")
    return saas_large_problem_type_data




def get_db(db):
    if db is None:
        db = mysql_base.Db()
    return db
