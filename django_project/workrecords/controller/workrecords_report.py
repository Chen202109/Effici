from django.shortcuts import render
from django.http import JsonResponse
from mydata import mysql_base
from workrecords.config import constant

from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime
from mydata import mysql_base



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

        db =mysql_base.Db()

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
              f'SUM(IF(`errortype` = "实施配置", 数量, 0)) AS sspz, '\
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
            myChart_xAxis.append(tableData[i]['softversion']) #数组，前端myChart 组件的xAxis 中data数据
            myChart_series.append(tableData[i]['total']) #数组，前端myChart 组件的series 中data数据

        # 给tableData最后一行加上合计
        summary = {key: 0 for key in func_list}
        summary["softversion"] = "合计"
        for i in range(1,len(func_list)):
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
