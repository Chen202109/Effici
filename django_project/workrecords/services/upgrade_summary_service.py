from datetime import datetime,timedelta
from mydata import mysql_base

from workrecords.config import constant

def get_saas_service_upgrade_trend(begin_date, end_date, function_name, resource_pool):
    """
    去查找指定的资源池的指定功能对应的几个service的升级和bug趋势
    """

    realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
    realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

    db = mysql_base.Db()

    service_list = constant.saas_function_service_map[function_name]
    # 查到的如果是那几个不重要的功能没什么对应的service，那就先跳过
    if not service_list:
        return []

    # 生成数据库查询时候对service的语句
    service_condition = ''
    if resource_pool != 'V3行业':
        for i in service_list:
            service_condition += f'microservicename LIKE "%{i}%" or '
        service_condition = service_condition[:-3]

    # 查询升级表，查看该资源池底下该服务的该时间范围内的升级时间
    sql = f' SELECT realdate, resourcepoolversion FROM upgradeplan_2023' \
          f' WHERE realdate >= "{realdate_begin}" AND realdate <= "{realdate_end}" ' \
          f' AND resourcepool = "{resource_pool}" ' \
          f' AND ({service_condition}) ' \
          f' ORDER BY realdate '

    # 这个是将所有符合条件的整行的升级数据的返回，可以用作查详细数据时候的缓存
    upgrade_record = db.select_offset(1, 2000, sql)
    # 这个是在指定资源池底下的这个服务的升级日期的list，list每个元素是字典，key是日期，value是0
    upgrade_time_record = [{'x': d["realdate"].split(' ')[0], 'version': "" if d['resourcepoolversion'][-4:] == "V3行业" else 'V' + '.'.join(
        [num for num in d['resourcepoolversion'][-4:]])} for d in upgrade_record if "realdate" in d]
    # 如果某两个字典的日期是一样的，那就是有一天同时两次的升级记录，他们version肯定也一样，将他们合并成一条
    upgrade_time_record = [item for i, item in enumerate(upgrade_time_record) if 'x' not in item or item['x'] not in [x['x'] for x in upgrade_time_record[:i]]]

    if resource_pool == 'V3行业':
        sql = f' SELECT * FROM workrecords_2023 ' \
              f' where createtime>="{begin_date}" ' \
              f' AND createtime<="{end_date}" ' \
              f' AND errorfunction= "{function_name}" ' \
              f' AND environment = "公有云" ' \
              f' AND softversion = "V3" ' \
              f' ORDER BY createtime '
    else:
        # 生成对受理问题查询时候省份条件的语句
        province_list = constant.source_pool_province_map[resource_pool]
        resource_pool_condition = ''
        for i in province_list:
            resource_pool_condition += f'region = "{i}" or '
        resource_pool_condition = resource_pool_condition[:-3]

        # 查询 work record 表，查询这段时间内选择的功能的受理问题记录
        table_name = "workrecords_2024" if begin_date >= "2024-01-01" else "workrecords_2023"
        sql = f' SELECT * FROM {table_name} ' \
              f' WHERE createtime>="{begin_date}" ' \
              f' AND createtime<="{end_date}" ' \
              f' AND errorfunction= "{function_name}" ' \
              f' AND environment = "公有云" ' \
              f' AND softversion != "V3" ' \
              f' AND ({resource_pool_condition}) ' \
              f' ORDER BY createtime '
    saas_problems = db.select_offset(1, 1000, sql)

    # 将受理问题查询出来的记录根据上面查询出来的升级时间点切割，然后赋值，每个时间点的值就是从这次升级到下次升级这个时间段内这个功能的受理次数
    # (remark: 因为比如一个大版本升级了，然后这个功能并没有升级，那么这个错的次数还是统计到上一次这个功能升级的数据点中，直到下一次这个功能升级了，
    # 所以折线图的数据点的值累加起来并不一定是这个版本这个功能受理了多少问题，而是着重在这次这个功能升级到下次这个功能升级之间对于这个升级，它出现了多少的问题)
    for i in range(len(upgrade_time_record)):
        time_range = (upgrade_time_record[i]['x'], end_date if i == len(upgrade_time_record) - 1 else upgrade_time_record[i + 1]['x'])
        upgrade_time_record[i]['y'] = len([d for d in saas_problems if time_range[0] < d["createtime"] <= time_range[1]])
    return upgrade_time_record


def get_saas_upgrade_resource_pool_summary(begin_date, end_date, resource_pool, version_list, db=None):

    data = []
    db = get_db(db)

    # 对这个资源池的升级次数按版本进行统计分类
    sql = f' SELECT resourcepoolversion, upgradetype, COUNT(*) as y from upgradeplan_2023 ' \
          f' WHERE plandate>="{begin_date}" AND plandate<="{end_date}" ' \
          f' AND resourcepool="{resource_pool}" ' \
          f' GROUP BY resourcepoolversion, upgradetype'
    upgrade_record = db.select_offset(1, 2000, sql)
    daily_upgrade_amount_record = [{
        'x': entry['x'],
        'y': next((item['y'] for item in upgrade_record if item['resourcepoolversion'] == "腾讯云-" + resource_pool + entry['x'][1:].replace(".", "")
                   and item["upgradetype"] == "日常"), 0)} for entry in version_list]
    added_daily_upgrade_amount_record = [{
        'x': entry['x'],
        'y': next((item['y'] for item in upgrade_record if item['resourcepoolversion'] == "腾讯云-" + resource_pool + entry['x'][1:].replace(".", "")
                   and item["upgradetype"] == "增值"), 0)} for entry in version_list]
    data.append({'seriesName': "日常升级次数", 'seriesData': daily_upgrade_amount_record})
    data.append({'seriesName': "增值升级次数", 'seriesData': added_daily_upgrade_amount_record})

    return data


def get_upgrade_error_type_summary(begin_date, end_date, system_name, db=None):
    resourcepool_sql = ""
    if system_name == "saas_v4":
        resourcepool_sql = 'AND resourcepool!="V3行业" AND resourcepool!="电子票夹" '
    elif system_name == "电子票夹":
        resourcepool_sql = ' AND resourcepool="电子票夹" '

    data = []
    db = get_db(db)

    # 由于realdate日期是2023-08-01 18:00:00 这种格式，所以对比时不等于2023-08-01 00:00:00，于是终止要+1天
    realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
    realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

    sql = 'SELECT ' \
          ' upgradetype, resourcepool, SUM(case when questiontype like "%bug%" then 1 else 0 end) AS 缺陷, ' \
          ' SUM(case when questiontype like "%需求%" then 1 else 0 end) AS 需求, ' \
          ' SUM(case when questiontype like "%优化%" then 1 else 0 end) AS 优化 ' \
          ' FROM upgradeplan_2023 ' \
          f' WHERE realdate >= "{realdate_begin}" AND realdate <= "{realdate_end}" ' \
          f'{resourcepool_sql} ' \
          ' GROUP BY upgradetype, resourcepool'
    saas_upgrade_problem_type_data = db.select_offset(1, 1000, sql)

    # 查出来格式是这样的：{'upgradetype': '增值', 'resourcepool': '01资源池', '缺陷': Decimal('31'), '需求': Decimal('13'), '优化': Decimal('2')}
    # 要进行转换成这样: {"saas_v4产品": "缺陷", '01资源池': '31', '02资源池': 'xx', '03资源池': 'xx', '04资源池': 'xx', '运营支撑平台': 'xx' }
    saas_daily_upgrade_problem_type_data = [{f"{system_name}标准产品": "缺陷"}, {f"{system_name}标准产品": "需求"}, {f"{system_name}标准产品": "优化"}]
    saas_added_upgrade_problem_type_data = [{f"{system_name}增值产品": "缺陷"}, {f"{system_name}增值产品": "需求"}, {f"{system_name}增值产品": "优化"}]
    for item in saas_upgrade_problem_type_data:
        if item['upgradetype'] == '日常':
            saas_daily_upgrade_problem_type_data[0][item["resourcepool"]] = item['缺陷']
            saas_daily_upgrade_problem_type_data[1][item["resourcepool"]] = item['需求']
            saas_daily_upgrade_problem_type_data[2][item["resourcepool"]] = item['优化']
        else:
            saas_added_upgrade_problem_type_data[0][item["resourcepool"]] = item['缺陷']
            saas_added_upgrade_problem_type_data[1][item["resourcepool"]] = item['需求']
            saas_added_upgrade_problem_type_data[2][item["resourcepool"]] = item['优化']

    data.append({'seriesName': f"{system_name}日常升级次数统计", 'seriesData': saas_daily_upgrade_problem_type_data})
    data.append({'seriesName': f"{system_name}增值升级次数统计", 'seriesData': saas_added_upgrade_problem_type_data})

    return data


def get_db(db):
    if db is None:
        db = mysql_base.Db()
    return db