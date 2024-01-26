from datetime import datetime,timedelta
from mydata import mysql_base
from collections import Counter
from workrecords.config import constant
import pandas as pd

from workrecords.services.data_dict_service import decode_data_item

def get_work_record_month_summary(begin_date, end_date):
    """
    查询传入的时间范围内每个月的受理数量，并且归纳那个月出错功能的前五
    :param begin_date 查询起始时间
    :param end_date 查询截止时间
    """
    db = mysql_base.Db()
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    sql = f' SELECT MONTH(createtime) AS Month, errorfunction, COUNT(*) AS ProblemAmount ' \
          f' FROM {table_name} ' \
          f' WHERE MONTH(createtime) between {datetime.strptime(begin_date, "%Y-%m-%d").month} AND {datetime.strptime(end_date, "%Y-%m-%d").month} ' \
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
    if len(month_function_list)!= 0:
        # 已经到查询的月份的末尾了跳出了，但是最后一个月份的数据还未进行sort和加入seriesData之中，进行添加
        month_function_list.sort(key=lambda x: x['amount'], reverse=True)
        series_data.append({'x': str(curr_month) + '月', 'y': month_amount, 'functionType': month_function_list[0:5]})
    return series_data

def get_work_record_version_function_summary(begin_date, end_date, province, function_list ):

    data = []

    db = mysql_base.Db()
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province!='全国' : condition_dict["region="] = province
    saas_version_data = db.select(["DISTINCT softversion as x"], table_name, condition_dict, " ORDER BY softversion ")

    for function_item in function_list:
        condition_dict["errorfunction="] = function_item
        saas_function_data = db.select(["softversion as x","COUNT(*) as y"], table_name, condition_dict, " GROUP BY softversion ")
        saas_version_data = [{'x': entry['x'], 'y': next((value['y'] for value in saas_function_data if value['x'] == entry['x']), 0)} for entry in saas_version_data]
        data.append({'seriesName': function_item, 'seriesData': saas_version_data})
    return data

def get_work_record_province_function_summary(begin_date, end_date, function_list):

    data = []
    db = mysql_base.Db()
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    region_list = db.select(["DISTINCT region as x"], table_name, condition_dict, "")
    saas_province_data = [{'x': d["x"], 'y': 0} for d in region_list if "x" in d]

    # 对每个功能进行查找
    for function_item in function_list:
        condition_dict["errorfunction="] = function_item
        saas_function_data = db.select(["*"], table_name, condition_dict, " ")
        saas_province_data = [{'x': entry['x'], 'y': Counter(item['region'] for item in saas_function_data)[entry['x']]} for entry in saas_province_data]
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
    data.append({"yMax": y_max})

    return data

def get_work_record_product_type_summary(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    condition_dict = {
        "createtime>=": begin_date,
        "createtime<=": end_date
    }
    if province != '全国': condition_dict["region="] = province
    saas_agency_type_data = db.select(["agentype as name", "count(*) as value"], table_name, condition_dict, " group by agentype ")
    return [{'seriesName': province + "受理行业种类", 'seriesData': saas_agency_type_data}]

def get_summary_item_amount(begin_date, end_date, province="全国", db=None):
    db = get_db(db)
    real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
    real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    province_condition_sql = "" if province=="全国" else f' AND region = "{province}" '

    work_record_table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
    
    # 对合计的数据进行统计添加
    sql = f'SELECT "受理问题合计" as name, count(*) as value from {work_record_table_name} WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'SELECT "V4 license受理合计" as name, count(*) from license_2023 WHERE authorizeddate >= "{begin_date}" AND authorizeddate <= "{end_date}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'select "私有化重大故障合计" as name, count(*) from majorrecords WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'select "生产监控问题合计" as name, count(*) from monitorrecords WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" {province_condition_sql} ' \
          f'UNION ALL ' \
          f'select "增值服务开通合计" as name, count(*) from orderprodct_2023 WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" {province_condition_sql} '
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
            while True:
                agency_amount += int(dataframe.loc[province, str(begin_time_month) + '月'])
                if begin_time_month == end_time_month:
                    break
                begin_time_month += 1
            break
        else:
            while begin_time_month <= 12:
                agency_amount += int(dataframe.loc[province, str(begin_time_month) + '月'])
                begin_time_month += 1
            begin_time_month = 1
            begin_time_year += 1
    # 对上线单位数量统计进行读取和插入到summary table中
    saas_country_summary_table_data.insert(0, {"name": '上线单位合计', "value": agency_amount})

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
    if begin_date< "2024-01-01":
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
    saas_soft_version_data = db.select(["softversion as x", "errorfunction", "count(*) as y"], table_name, condition_dict, " group by softversion, errorfunction ")

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
    saas_province_problem_data = db.select([f"region as {region_alias}", f"count(*) as {value_alias}"], table_name, condition_dict," group by region ")
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
    data = []
    data.append({'seriesName': "全国受理数量", 'seriesData': saas_country_data})
    data.append({"valueMax": value_max})
    return data

def get_work_record_province_agency_summary():
    print()




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