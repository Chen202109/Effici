from django.shortcuts import render
from django.http import JsonResponse
from mydata import mysql_base
from collections import Counter
from workrecords.config import constant

from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime

import json
from mydata import mysql_base
import pandas as pd

# ----------------------------------------------------------- AnalysisUpgradeTrend.vue 的请求 --------------------------------------------

def analysis_saas_upgrade_problem_type(request):
    """
    分析升级数据和所属问题分类的对比
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        # 由于realdate日期是2023-08-01 18:00:00 这种格式，所以对比时不等于2023-08-01 00:00:00，于是终止要+1天
        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        db =mysql_base.Db()

        sql = 'SELECT '\
              ' upgradetype, resourcepool, SUM(case when questiontype like "%bug%" then 1 else 0 end) AS 缺陷, '\
              ' SUM(case when questiontype like "%需求%" then 1 else 0 end) AS 需求, '\
              ' SUM(case when questiontype like "%优化%" then 1 else 0 end) AS 优化 '\
              ' FROM upgradeplan_2023 ' \
              f' WHERE realdate >= "{realdate_begin}" AND realdate <= "{realdate_end}" '\
              ' GROUP BY upgradetype, resourcepool'
        saas_upgrade_problem_type_data = db.select_offset(1, 1000, sql)

        # 查出来格式是这样的：{'upgradetype': '增值', 'resourcepool': '01资源池', '缺陷': Decimal('31'), '需求': Decimal('13'), '优化': Decimal('2')}
        # 要进行转换成这样: {"saas_v4产品": "缺陷", '01资源池': '31', '02资源池': 'xx', '03资源池': 'xx', '04资源池': 'xx', '运营支撑平台': 'xx' }
        saas_daily_upgrade_problem_type_data  = [{"saas_v4标准产品": "缺陷"}, {"saas_v4标准产品": "需求"}, {"saas_v4标准产品": "优化"}]
        saas_added_upgrade_problem_type_data  = [{"saas_v4增值产品": "缺陷"}, {"saas_v4增值产品": "需求"}, {"saas_v4增值产品": "优化"}]
        for item in saas_upgrade_problem_type_data:
            if item['upgradetype'] == '日常':
                saas_daily_upgrade_problem_type_data[0][item["resourcepool"]] = item['缺陷']
                saas_daily_upgrade_problem_type_data[1][item["resourcepool"]] = item['需求']
                saas_daily_upgrade_problem_type_data[2][item["resourcepool"]] = item['优化']
            else:
                saas_added_upgrade_problem_type_data[0][item["resourcepool"]] = item['缺陷']
                saas_added_upgrade_problem_type_data[1][item["resourcepool"]] = item['需求']
                saas_added_upgrade_problem_type_data[2][item["resourcepool"]] = item['优化']

        data.append({'seriesName': "公有云saas_v4日常升级次数统计", 'seriesData': saas_daily_upgrade_problem_type_data})
        data.append({'seriesName': "公有云saas_v4增值升级次数统计", 'seriesData': saas_added_upgrade_problem_type_data})
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_service_upgrade_trend(request):
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        resource_pools = request.GET.get('resourcePool').split(',')
        function_names = request.GET.get('function_name').split(',')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        for i in range(len(resource_pools)):
            for j in range(len(function_names)):
                data.append({'service': resource_pools[i] + '-' + function_names[j], 
                             'data': find_service_upgrade_trend(begin_date, end_date, realdate_begin, realdate_end, function_names[j], resource_pools[i])})

    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def find_service_upgrade_trend(begin_date, end_date, realdate_begin, realdate_end, function_name, resource_pool):
    """
    去查找指定的资源池的指定功能对应的几个service的升级和bug趋势
    """

    db =mysql_base.Db()

    service_list = constant.saas_function_service_map[function_name]
    # 查到的如果是那几个不重要的功能没什么对应的service，那就先跳过
    if service_list == []:
        return []
    
    # 生成数据库查询时候对service的语句, 如果是V3，需要对应的服务,先用1=1跳过该条件
    service_condition = ''
    if resource_pool != 'V3行业':
        for i in service_list:
            service_condition += f'microservicename LIKE "%{i}%" or '
        service_condition = service_condition[:-3]
    else:
        service_condition = "1=1"

    # 查询升级表，查看该资源池底下该服务的该时间范围内的升级时间  
    sql = f' SELECT * FROM upgradeplan_2023' \
          f' WHERE realdate >= "{realdate_begin}" AND realdate <= "{realdate_end}" ' \
          f' AND resourcepool = "{resource_pool}" ' \
          f' AND ({service_condition}) '\
          f' ORDER BY realdate '
    
    # 这个是将所有符合条件的整行的升级数据的返回，可以用作查详细数据时候的缓存
    upgrade_record = db.select_offset(1, 2000, sql)
    # 这个是在指定资源池底下的这个服务的升级日期的list，list每个元素是字典，key是日期，value是0
    upgrade_time_record = [{'x':d["realdate"].split(' ')[0], 'version': "" if d['resourcepoolversion'][-4:] =="V3行业" else 'V'+'.'.join([num for num in d['resourcepoolversion'][-4:]])} for d in upgrade_record if "realdate" in d]
    # 如果某两个字典的日期是一样的，那就是有一天同时两次的升级记录，他们version肯定也一样，将他们合并成一条
    upgrade_time_record = [item for i, item in enumerate(upgrade_time_record) if 'x' not in item or item['x'] not in [x['x'] for x in upgrade_time_record[:i]]]

    if resource_pool == 'V3行业':
        sql = f' SELECT * FROM workrecords_2023 '\
          f' where createtime>="{begin_date}" '\
          f' AND createtime<="{end_date}" '\
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
        sql = f' SELECT * FROM workrecords_2023 '\
            f' WHERE createtime>="{begin_date}" '\
            f' AND createtime<="{end_date}" '\
            f' AND errorfunction= "{function_name}" ' \
            f' AND environment = "公有云" ' \
            f' AND softversion != "V3" ' \
            f' AND ({resource_pool_condition}) ' \
            f' ORDER BY createtime '
    
    saasProblems = db.select_offset(1, 1000, sql)
    
    # 将受理问题查询出来的记录根据上面查询出来的升级时间点切割，然后赋值，每个时间点的值就是从这次升级到下次升级这个时间段内这个功能的受理次数
    # (remark: 因为比如一个大版本升级了，然后这个功能并没有升级，那么这个错的次数还是统计到上一次这个功能升级的数据点中，直到下一次这个功能升级了，
    # 所以折线图的数据点的值累加起来并不一定是这个版本这个功能受理了多少问题，而是着重在这次这个功能升级到下次这个功能升级之间对于这个升级，它出现了多少的问题)
    for i in range(len(upgrade_time_record)):
        time_range = (upgrade_time_record[i]['x'], end_date if i==len(upgrade_time_record)-1 else upgrade_time_record[i+1]['x'])
        upgrade_time_record[i]['y'] = len([d for d in saasProblems if time_range[0] < d["createtime"] <= time_range[1]])
    
    return upgrade_time_record


def analysis_version_problem_by_resource_pool(request):
    """
    分析版本信息和bug的趋势对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        resource_pools = request.GET.get('resourcePool').split(',')
        function_names = request.GET.get('function_name').split(',')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 先获取这段时间内的有哪些版本
        sql = f'SELECT DISTINCT softversion from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" AND softversion != "V3"  ORDER BY softversion '
        soft_version_list = db.select_offset(1, 2000, sql)
        saas_version_data = [{'x':d["softversion"], 'y':0} for d in soft_version_list if "softversion" in d]

        for resource_pool in resource_pools: 
            # 生成对受理问题查询时候省份条件的语句
            province_list = constant.source_pool_province_map[resource_pool]
            resource_pool_condition = ''
            for i in province_list:
                resource_pool_condition += f'region = "{i}" or '
            resource_pool_condition = resource_pool_condition[:-3]

            # 对每个功能的受理问题进行统计
            for function_name in function_names:
                # 查询 work record 表，查询这段时间内选择的功能的受理问题记录
                sql = f' SELECT * FROM workrecords_2023 '\
                    f' WHERE createtime>="{begin_date}" AND createtime<="{end_date}" '\
                    f' AND errorfunction= "{function_name}" ' \
                    f' AND environment = "公有云" ' \
                    f' AND softversion != "V3" ' \
                    f' AND ({resource_pool_condition}) ' \
                    f' ORDER BY createtime '
                saas_function_data = db.select_offset(1, 2000, sql)

                saas_version_data = [{'x': entry['x'], 'y': Counter(item['softversion'] for item in saas_function_data)[entry['x']]} for entry in saas_version_data]
                data.append({'seriesName': function_name, 'seriesData': saas_version_data})
            
            # 对这个资源池的升级次数按版本进行统计分类
            sql = f' SELECT DISTINCT resourcepoolversion, upgradetype, COUNT(*) as upgradeAmount from upgradeplan_2023 '\
                  f' WHERE plandate>="{begin_date}" AND plandate<="{end_date}" '\
                  f' AND resourcepool="{resource_pool}" '\
                  f' GROUP BY resourcepoolversion, upgradetype'
            upgrade_record = db.select_offset(1, 2000, sql)
            daily_upgrade_amount_record = [{'x': entry['x'], 'y': next((item['upgradeAmount'] for item in upgrade_record if item['resourcepoolversion'] == "腾讯云-"+ resource_pool + entry['x'][1:].replace(".", "") and item["upgradetype"] == "日常"),0)} for entry in saas_version_data]
            added_daily_upgrade_amount_record    = [{'x': entry['x'], 'y': next((item['upgradeAmount'] for item in upgrade_record if item['resourcepoolversion'] == "腾讯云-"+ resource_pool + entry['x'][1:].replace(".", "") and item["upgradetype"] == "增值"),0)} for entry in saas_version_data]
            data.append({'seriesName': "日常升级次数", 'seriesData': daily_upgrade_amount_record})
            data.append({'seriesName': "增值升级次数", 'seriesData': added_daily_upgrade_amount_record})

    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisUpgradeTrend.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisLargeProblemData.vue 的请求 --------------------------------------------

def analysis_saas_large_problem_province_list(request):
    """
    获取私有化重大问题的省份
    """
    data = []

    if request.method == 'GET':

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region from majorrecords'
        saas_large_problem_province_list = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "监控出错省份", 'seriesData': saas_large_problem_province_list})
 
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_large_problem_by_function_and_province(request):
    """
    分析私有化重大故障的出错功能和省份的对比
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        province = request.GET.get('provinceSelected', default='')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct errortype as x, count(*) as y from majorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" and region = "{province}" group by errortype '
        saas_large_problem_function_problem_by_province_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': province+"监控出错功能", 'seriesData': saas_large_problem_function_problem_by_province_data})

            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_large_problem_by_province(request):
    """
    分析私有化重大故障的问题数量的省份对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region as x, count(*) as y from majorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by region '
        saas_large_problem_province_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "问题受理数量", 'seriesData': saas_large_problem_province_problem_data})
     
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_large_problem_by_function(request):
    """
    分析出现的重大生产故障的问题分类
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
        sql = f' SELECT errortype as name, count(*) as value from majorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by name'
        saas_large_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "私有化重大故障问题分类", 'seriesData': saas_large_problem_data})

        # 进行排序，找出top10, 并且加上总数
        total = sum(item['value'] for item in saas_large_problem_data)
        sorted_data = sorted(saas_large_problem_data, key=lambda x : x['value'], reverse = True)[0:10]
        for item in sorted_data: item['percent'] = f"{((item['value'] / total) * 100):.2f}%" if total!=0 else 0
        data.append({'seriesName': "私有化重大故障top10", 'seriesData': sorted_data})
        data.append({'seriesName': "私有化重大故障数量合计", 'seriesData': total})
        
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisLargeProblemData.vue 的请求 --------------------------------------------

# ----------------------------------------------------------- AnalysisMonitorProblem.vue 的请求 --------------------------------------------

def analysis_saas_monitor_province_list(request):
    """
    获取监控异常这边的省份
    """
    data = []

    if request.method == 'GET':

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region from monitorrecords'
        saas_minitor_province_list = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "监控出错省份", 'seriesData': saas_minitor_province_list})
 
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_monitor_problem_by_function_and_province(request):
    """
    分析生产环境监控异常的出错功能和省份的对比
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        province = request.GET.get('provinceSelected', default='')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct errortype as x, count(*) as y from monitorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" and region = "{province}" group by errortype '
        saas_minitor_function_problem_by_province_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': province+"监控出错功能", 'seriesData': saas_minitor_function_problem_by_province_data})

            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_monitor_problem_by_province(request):
    """
    分析生产环境监控异常的问题数量的省份对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region as x, count(*) as y from monitorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by region '
        saas_minitor_province_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "问题受理数量", 'seriesData': saas_minitor_province_problem_data})

            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_minitor_problem_by_function(request):
    """
    分析省份出现的重大生产故障的数量
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
        sql = f' SELECT errortype as name, count(*) as value from monitorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by name'
        saas_monitor_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "生产监控异常问题分类", 'seriesData': saas_monitor_problem_data})

        # 进行排序，找出top10, 并且加上总数
        total = sum(item['value'] for item in saas_monitor_problem_data)
        sorted_data = sorted(saas_monitor_problem_data, key=lambda x : x['value'], reverse = True)[0:10]
        for item in sorted_data: item['percent'] = f"{((item['value'] / total) * 100):.2f}%" if total!=0 else 0
        data.append({'seriesName': "生产监控异常问题top10", 'seriesData': sorted_data})
        data.append({'seriesName': "生产监控异常问题合计", 'seriesData': total})
        
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisMonitorProblem.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisAddedServiceData.vue 的请求 --------------------------------------------

def analysis_saas_added_service_province_list(request):
    """
    获取增值服务这边的省份
    """
    data = []

    if request.method == 'GET':
        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region from orderprodct_2023'
        saas_added_service_province_list = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "增值服务订购省份", 'seriesData': saas_added_service_province_list})
 
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_added_service_by_function_and_province(request):
    """
    分析增值服务订购的的服务类别和省份的对比
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        province = request.GET.get('provinceSelected', default='')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct ordername as x, count(*) as y from orderprodct_2023 WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" and region = "{province}" group by ordername '
        saas_added_service_function_problem_by_province_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': province+"增值服务类别", 'seriesData': saas_added_service_function_problem_by_province_data})

            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_added_service_by_province(request):
    """
    分析增值服务开通的省份对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region as x, count(*) as y from orderprodct_2023 WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by region '
        saas_minitor_province_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "增值服务开通数量", 'seriesData': saas_minitor_province_problem_data})

            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_added_service_by_function(request):
    """
    分析增值服务的服务分类对比
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
        sql = f' SELECT ordername as name, count(*) as value from orderprodct_2023 WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by name'
        saas_monitor_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "增值服务分类", 'seriesData': saas_monitor_problem_data})

        # 进行排序，找出top10, 并且加上总数
        total = sum(item['value'] for item in saas_monitor_problem_data)
        sorted_data = sorted(saas_monitor_problem_data, key=lambda x : x['value'], reverse = True)[0:10]
        for item in sorted_data: item['percent'] = f"{((item['value'] / total) * 100):.2f}%" if total!=0 else 0
        data.append({'seriesName': "增值服务top10", 'seriesData': sorted_data})
        data.append({'seriesName': "增值服务合计", 'seriesData': total})
        
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisAddedServiceData.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisPrivatizationLicense.vue 的请求 --------------------------------------------

def analysis_saas_privatization_license_register_province(request):
    """
    分析私有化license开通数量的省份的数据
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        db =mysql_base.Db()
        sql = f'select DISTINCT region,COUNT(DISTINCT agenname) as count from license_2023 where authorizeddate>="{begin_date}" and authorizeddate<="{end_date}" GROUP BY region ORDER BY count desc'
        license_register_province_data = db.select_offset(1, 1000, sql)
        # 这个是查询后返回的数据，类似 [{'region': '上海', 'count': 2}, {'region': '北京', 'count': 1}]
        # 将上面的转成下面这种，这样前端才能挂到license_data里面
        # [{'上海': 2, '北京':3, '广东':3}]  
        # 生成要转化成的数据类型, 并加入表头表尾
        license_data = [{"省份": "单位申请数"}]
        sumLicenseRegister = 0
        for item in license_register_province_data:
            sumLicenseRegister += item["count"]
            license_data.append({item["region"]: item["count"]})
        license_data.append({"合计": sumLicenseRegister})


        data.append({'seriesName': "v4 license受理数据统计", 'seriesData': license_data})

            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisPrivatizationLicense.vue 的请求 --------------------------------------------

if __name__ == '__main__':
    pass