from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from mydata import mysql_base
from collections import Counter
from . import constant

from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime

import json
from mydata import mysql_base


# ----------------------------------------------------------- AnalysisData.vue 的请求 ----------------------------------------------------

def work_record_detail_search(request):
    # 如果请求为get 则进行查询
    # 将接受到的数据放入selet_parme
    # select_prame = {
    #     'page': 1,  # 第几页
    #     'page_size': 10,  # 每页多少条
    #     'begintime': '2023-07-10',  # 查询起始日期
    #     'endtime': '2023-07-20',  # 查询终止日期
    #     'version': 'V4.0.4.0'  # 版本号
    # }
    # 判断请求类型
    if request.method == 'GET':
        # 获得GET请求后面的参数信息
        search_filter = request.GET.get('searchFilter')
        search_filter = json.loads(search_filter)
        print(f'收到的参数为{search_filter}')
        print(f'收到的起始：{search_filter["beginData"]} 和结尾 {search_filter["endData"]}')

        realdate_begin = datetime.strptime(search_filter["beginData"], '%Y-%m-%d')
        realdate_end = datetime.strptime(search_filter["endData"], '%Y-%m-%d') + timedelta(days=1)
        
        isSolvedSql = "" if search_filter["isSolved"] == "" else f'AND issolve = "{search_filter["isSolved"]}"'
        errorFunctionSql = "" if search_filter["errorFunction"] == "" else f'AND errorfunction = "{search_filter["errorFunction"]}"'
        errorTypeSql = "" if search_filter["errorType"] == "" else f'AND errortype = "{search_filter["errorType"]}"'
        softVersionSql = "" if search_filter["softVersion"] == "" else f'AND softversion = "{search_filter["softVersion"]}"'
        problemDescriptionSql = "" if search_filter["problemDescription"] == "" else f'AND problem LIKE "%{search_filter["problemDescription"]}%"'

        db =mysql_base.Db()
        sql = f' SELECT * from workrecords_2023 ' \
              f' WHERE createtime>="{realdate_begin}" and createtime<="{realdate_end}" '\
              f' {isSolvedSql} {errorFunctionSql} {errorTypeSql} {softVersionSql} {problemDescriptionSql} '\
              f' ORDER BY createtime'
        results = db.select_offset(1, 1000, sql)

    return JsonResponse({'data': results}, json_dumps_params={'ensure_ascii': False})

def analysisselect(request):
    analysisData={
        'tableData': [],
        'licenseData': []
    }
    # 判断请求类型
    if request.method == 'GET':
        # 获得GET请求后面的参数信息
        beginData = request.GET.get('beginData', default='2023-07-01')
        endData = request.GET.get('endData', default='2023-07-31')

        #■■■ 开始分页查询，获得对应时间范围内，license的申请数据
        db =mysql_base.Db()
        sql = f'select DISTINCT region,COUNT(DISTINCT agenname) as count from license_2023 where authorizeddate>="{beginData}" and authorizeddate<="{endData}" GROUP BY region'
        licenseData_list = db.select_offset(1, 1000, sql)
        # 这个是查询后返回的数据，类似 [{'region': '上海', 'count': 2}, {'region': '北京', 'count': 1}]
        # 将上面的转成下面这种，这样前端才能挂到license_data里面
        # [{'上海': 2, '北京':3, '广东':3}]  注：license_data数组只是 前端的analysisData字典的一部分 analysisData['license_data']

        # 生成要转化成的数据类型并进行倒序排序
        license_data = [{k: v} for k, v in sorted({d["region"] : d["count"] for d in licenseData_list}.items(), key=lambda item:item[1], reverse=True)]
        # 因为加入头部的表头和合计的表尾
        license_data.insert(0, {"省份": "单位申请数"})
        license_data.append({"合计": sum(item["count"] for item in licenseData_list)})
        analysisData['licenseData'] = license_data
        
        # ■■■ 结束license的数据获取


        # ■■■ 开始分页查询，获得对应时间范围内，【数据汇报】--->受理问题的表格数据
        # total是每个版本的受理数量合计，其他用了 列传行 的办法
        sql = f'SELECT softversion as softversion,' \
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
              f'SUM(IF(`errortype` = "实施配置", 数量, 0)) AS sspz, '\
              f'SUM(IF(`errortype` = "异常数据处理", 数量, 0)) AS ycsjcl ' \
              f'FROM' \
              f'(select softversion , errorfunction, errortype, count(*) as 数量 ' \
              f'from workrecords_2023 where createtime>="{beginData}" and createtime<="{endData}" ' \
              f'GROUP BY softversion, errorfunction, errortype ) A ' \
              f'GROUP BY softversion'
        tableData = db.select_offset(1, 1000, sql)

        # 【数据汇报】--->受理问题的柱形图
        # 将 tableData 查询的数据中，softversion的内容组装到一个数组中给前端myChart柱形图setOption传参
        # myChart_xAxis表示softversion版本号 和 myChart_series表示total合计数量
        myChart_xAxis = []
        myChart_series = []
        for i in range(len(tableData)):
            myChart_xAxis.append(tableData[i]['softversion']) #数组，前端myChart 组件的xAxis 中data数据
            myChart_series.append(tableData[i]['total']) #数组，前端myChart 组件的series 中data数据

        # 给tableData最后一行加上合计
        func_list = ["softversion", "total", "report", "openbill", "licenseReset", "added", "collection", "exchange", "writeoff", 
                     "billManagement", "security", "print", "datasync", "inverse", "opening", "softbug", "sspz", "ycsjcl"]
        summary = {}
        summary["softversion"] = "合计"
        for i in range(1,len(func_list)):
            val = 0
            for item in tableData:
                val += item[func_list[i]]
            summary[func_list[i]] = val        
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

        analysisData['annularChart_data'] =  annularChart_data # 添加数组元素 【数据汇报】---> 饼状图形数据
        # ■■■ 结束 受理问题 相关的数据获取

        # ■■■ 开始分页查询，获得对应时间范围内，【数据汇报】--->升级计划表格数据
        # print('beginData类型',type(beginData)) 得到是str
        # 由于realdate日期是2023-08-01 18:00:00 这种格式，所以对比时不等于2023-08-01 00:00:00，于是终止要+1天
        realdate_begin = datetime.strptime(beginData, '%Y-%m-%d')
        realdate_end = datetime.strptime(endData, '%Y-%m-%d') + timedelta(days=1)

        sql = f'SELECT A.resourcepool, upgradetype, ' \
              f'SUM(IF(LOCATE("bug", A.questiontype) > 0, A.数量, 0)) AS 缺陷, ' \
              f'SUM(IF(LOCATE("需求", A.questiontype) > 0, A.数量, 0)) AS 需求, ' \
              f'SUM(IF(LOCATE("优化", A.questiontype) > 0, A.数量, 0)) AS 优化, ' \
              f'SUM(A.升级次数) as 升级次数 ' \
              f'FROM ' \
              f'(SELECT resourcepool, upgradetype,COUNT(*) AS 升级次数, "" AS questiontype, 0 AS 数量 ' \
              f' FROM upgradeplan_2023 ' \
              f' WHERE realdate >= "{realdate_begin}" AND realdate <= "{realdate_end}" ' \
              f' GROUP BY resourcepool,upgradetype ' \
              f' UNION ALL ' \
              f' SELECT B.resourcepool,upgradetype, 0 AS 升级次数, B.questiontype, B.数量 ' \
              f' FROM ' \
              f' (SELECT resourcepool, upgradetype,questiontype, COUNT(*) AS 数量 ' \
              f' FROM upgradeplan_2023 ' \
              f' WHERE realdate >= "{realdate_begin}" AND realdate <= "{realdate_end}" ' \
              f' GROUP BY resourcepool,upgradetype, questiontype ' \
              f' ) B ' \
              f') A ' \
              f'GROUP BY A.resourcepool,upgradetype'
        upgradeData = db.select_offset(1, 1000, sql)
        analysisData['upgradeData'] = upgradeData  # 添加数组元素 【数据汇报】--->升级计划的内容
        # ■■■ 结束 升级计划 相关的数据获取

    return JsonResponse({'data': analysisData}, json_dumps_params={'ensure_ascii': False})

def analysis_saas_problem_type_in_versions(request):
    """
    数据汇报界面的， 产品bug, 实施配置，异常数据处理，和各版本和功能的详细对比
    """
    problem_type_list = ["产品bug", "实施配置", "异常数据处理"]
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        db =mysql_base.Db()

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
                new_item = { problem_type : function_type }
                total = 0 
                for item in saas_problem_type_and_function_data:
                    # 因为前端那边的el-table，如果是V4.3.2.0这样有带.的，他会没办法自动把数值放上去，所以这边为了前端的格式需要将之转化成V4_3_2_0
                    new_item[item["softversion"].replace(".", "_")] = int(item[function_type]) 
                    total += int(item[function_type])
                new_item["合计"] = total
                saas_problem_type_and_function_data_in_version.append(new_item)
                
                
            data.append({'problemType': problem_type, 'problemTypeData': saas_problem_type_and_function_data_in_version})
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisData.vue 的请求 ----------------------------------------------------

# ----------------------------------------------------------- AnalysisUpgrade_version.vue 的请求 --------------------------------------------

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


def analysis_version_upgrade_trend(request):
    """
    分析版本信息和bug的趋势对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        function_name = request.GET.get('function_name').split(',')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        sql = f'SELECT DISTINCT softversion from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" ORDER BY softversion '
        soft_version_list = db.select_offset(1, 2000, sql)
        saas_version_data = [{'x':d["softversion"], 'y':0} for d in soft_version_list if "softversion" in d]

        for i in range(len(function_name)):
            sql = f' SELECT * from workrecords_2023 '\
                  f' WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" '\
                  f' AND errorfunction = "{function_name[i]}" '
            saas_function_data = db.select_offset(1, 2000, sql)
            saas_version_data = [{'x': entry['x'], 'y': Counter(item['softversion'] for item in saas_function_data)[entry['x']]} for entry in saas_version_data]
            data.append({'seriesName': function_name[i], 'seriesData': saas_version_data})
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_function_by_province(request):
    """
    分析省份受理的功能的问题数量的对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        function_name = request.GET.get('function_name').split(',')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        sql = f'SELECT DISTINCT region as x  from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" '
        region_list = db.select_offset(1, 2000, sql)
        saas_province_data = [{'x':d["x"], 'y':0} for d in region_list if "x" in d]

        # 对每个功能进行查找
        for i in range(len(function_name)):
            sql = f' SELECT * from workrecords_2023 '\
                  f' WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" '\
                  f' AND errorfunction = "{function_name[i]}" '
            saas_function_data = db.select_offset(1, 2000, sql)
            saas_province_data = [{'x': entry['x'], 'y': Counter(item['region'] for item in saas_function_data)[entry['x']]} for entry in saas_province_data]
            data.append({'seriesName': function_name[i], 'seriesData': saas_province_data})
        
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
        for i in range(len(function_name)):
            data[i]['seriesData'] = [next(filter(lambda x: x['x'] == region, data[i]['seriesData'])) for region in sorted_region_x]

        # 加上yMax的值，该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
        data.append({"yMax": y_max})
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_problem_by_province_agency(request):
    """
    分析省份受理的问题数量的对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region as x, count(*) as y from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" group by region '
        saas_province_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "问题受理数量", 'seriesData': saas_province_problem_data})

        # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
        sql = f' SELECT distinct region as x, count(*) as y from majorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" group by region '
        saas_large_problem_data = db.select_offset(1, 2000, sql)
        # 生成一个顺序与saas_province_problem_data一致的数组,如果重大故障查询的没有那个省份，则那个省份的y值为0，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
        saas_province_large_problem_data_inorder = [{'x': prov['x'], 'y': next((value['y'] for value in saas_large_problem_data if value['x'] == prov['x']), 0)} for prov in saas_province_problem_data]
        data.append({'seriesName': "私有化重大故障数量", 'seriesData': saas_province_large_problem_data_inorder})

        import pandas as pd
        # 对上线单位数量统计进行读取
        dataframe = pd.read_csv('./workrecords/existedAgencyAccountByProvince.csv',sep=',').rename(columns={'省份':'x','数量':'y'}).to_dict(orient="records")
        # 生成一个顺序与saas_province_problem_data一致的数组，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
        # 新数组的x值通过saas_province_problem_data获取，y的值通过dataFrame读取的上线单位的数量进行填入。
        # 如果是这一行报错StopIteration，基本上就是登记的时候省份没有登记对，比如内蒙古写成内蒙，需要去数据库进行调整让省份和workrecords/existedAgencyAccountByProvince.csv的省份名称一致
        print()
        print(saas_province_problem_data)
        print(dataframe)
        print()
        saas_province_agency_account_data = [{**prov, 'y': next(filter(lambda ag: ag['x'] == prov['x'], dataframe))['y']} for prov in saas_province_problem_data]
        data.append({'seriesName': "上线单位数量", 'seriesData': saas_province_agency_account_data})
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_problem_by_month(request):
    """
    分析某一年月份受理的问题数量的对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        saas_month_data = []

        db =mysql_base.Db()
        sql = f'SELECT MONTH(createtime) AS Month,COUNT(*) AS ProblemAmount FROM workrecords_2023 WHERE MONTH(createtime) between {datetime.strptime(begin_date, "%Y-%m-%d").month} and {datetime.strptime(end_date, "%Y-%m-%d").month} GROUP BY MONTH(createtime)'
        saas_month_data = db.select_offset(1, 2000, sql)
        seriesData = [{'x':str(d["Month"])+'月', 'y':d["ProblemAmount"]} for d in saas_month_data]
        data.append({'seriesName': "问题受理数量", 'seriesData': seriesData})
            
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

# ----------------------------------------------------------- AnalysisUpgrade_version.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisThirdPartyProblem.vue 的请求 --------------------------------------------

def analysis_saas_monitor_province_list(request):
    """
    获取监控异常这边的省份
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]  
        sql = f' SELECT distinct region from monitorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" '
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

# ----------------------------------------------------------- AnalysisThirdPartyProblem.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisAddedServiceData.vue 的请求 --------------------------------------------

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


# ----------------------------------------------------------- AnalysisCountryData.vue 的请求 --------------------------------------------

def analysis_saas_problem_by_country(request):
    """
    分析每个省份的受理数量，给全国地图使用
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()
        # 查询数据库的所有region并放入数组中
        sql = f' SELECT distinct region as name, count(*) as value from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" group by region '
        saas_province_problem_data = db.select_offset(1, 2000, sql)
        
        # 生成关于全国省份的数据
        saas_country_data = []
        # 用于visualMap使用，显示颜色渐变，给这个组件提供一个数据的最大值
        value_max = 0
        for prov in constant.china_province_list:
            value = next((item['value'] for item in saas_province_problem_data if item['name'] == prov), 0)
            value_max = value if value > value_max else value_max
            #  数组格式为[{"name":"省份名称","value":受理问题的数量}] ， 因为echarts地图他使用的数据格式是name和value，所以得对应上不能自定义值
            saas_country_data.append({'name':prov, 'value': value})
        data.append({'seriesName': "全国省份受理数据", 'seriesData': saas_country_data})
        data.append({"valueMax": value_max})
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})

# ----------------------------------------------------------- AnalysisCountryData.vue 的请求 --------------------------------------------


if __name__ == '__main__':
    pass