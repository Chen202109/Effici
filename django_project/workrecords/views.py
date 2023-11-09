from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from mydata import mysql_base
from . import constant

from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime

import json
from mydata import mysql_base


# Create your views here.
# 创建处理函数信息
def select(request):
    # 如果请求为post 则进行查询
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
        beginData = request.GET.get('beginData',default='2023-07-01')
        endData = request.GET.get('endData', default='2023-07-31')
        problem = request.GET.get('problem', default='')
        errortype = request.GET.get('errortype',default='')

        print(f'收到的problem为{problem}')
        if problem != "":
            problem = f'and problem like "%{problem}%"'

        if errortype != "":
            errortype = f'and errortype = "{errortype}"'

        # 分页查询
        db =mysql_base.Db()
        sql = f'select * from workrecords_2023 where createtime>="{beginData}" and createtime<="{endData}" {problem} {errortype}order by createtime'
        results = db.select_offset(1, 1000, sql)
        # print(type(results), len(results),results)

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
        # [{'上海': 2, '北京':3}]  注：license_data数组只是 前端的analysisData字典的一部分 analysisData['license_data']

        license_dict = {} # 用于保存数组内的字典 , 像这样 [{'上海': 2, '北京':3}]
        for i in range(len(licenseData_list)): # 循环次数为查询出来的sql返回的dict，注意select都是返回dict
            license_region = licenseData_list[i]['region'] # 获得
            license_count = licenseData_list[i]['count']
            license_dict[f'{license_region}']=license_count # 添加字典元素

        analysisData['licenseData'].append(license_dict) # 添加数组元素 license申请的内容
        print(f'当前license数据 {analysisData["licenseData"]}')
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
        print(type(annularChart_data),f'annularChart_data{annularChart_data}')

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

        # print(f'tableData 返回 {tableData}')
        # print(type(analysisData), len(analysisData), analysisData)

    return JsonResponse({'data': analysisData}, json_dumps_params={'ensure_ascii': False})


def analysis_service_upgrade_trend(request):
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        resource_pool = request.GET.get('resourcePool').split(',')
        function_name = request.GET.get('function_name').split(',')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        for i in range(len(resource_pool)):
            for j in range(len(function_name)):
                data.append({'service': resource_pool[i] + '-' + function_name[j], 
                             'data': find_service_upgrade_trend(begin_date, end_date, realdate_begin, realdate_end, function_name[j], resource_pool[i])})

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
    upgrade_record = db.select_offset(1, 1000, sql)
    # 这个是在指定资源池底下的这个服务的升级日期的list，list每个元素是字典，key是日期，value是0
    upgrade_time_record = [{'x':d["realdate"].split(' ')[0], 'version': "" if d['resourcepoolversion'][-4:] =="V3行业" else 'V'+'.'.join([num for num in d['resourcepoolversion'][-4:]])} for d in upgrade_record if "realdate" in d]
    # 如果某两个字典的日期是一样的，那就是有一天同时两次的升级记录，他们version肯定也一样，将他们合并成一条
    upgrade_time_record = [item for i, item in enumerate(upgrade_time_record) if 'x' not in item or item['x'] not in [x['x'] for x in upgrade_time_record[:i]]]
    print(upgrade_time_record)

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
            f' where createtime>="{begin_date}" '\
            f' AND createtime<="{end_date}" '\
            f' AND errorfunction= "{function_name}" ' \
            f' AND environment = "公有云" ' \
            f' AND softversion != "V3" ' \
            f' AND ({resource_pool_condition}) ' \
            f' ORDER BY createtime '
    
    saasProblems = db.select_offset(1, 1000, sql)
    
    # 将受理问题查询出来的记录根据上面查询出来的升级时间点切割，然后赋值，每个时间点的值就是从这次升级到下次升级这个时间段内这个功能的受理次数
    for i in range(len(upgrade_time_record)):
        time_range = (upgrade_time_record[i]['x'], end_date if i==len(upgrade_time_record)-1 else upgrade_time_record[i+1]['x'])
        upgrade_time_record[i]['y'] = len([d for d in saasProblems if time_range[0] < d["createtime"] <= time_range[1]])

    print(upgrade_time_record)
    return upgrade_time_record


def analysis_version_upgrade_trend(request):
    """
    分析版本信息和bug的趋势对比。
    """
    data = []
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


if __name__ == '__main__':
    pass