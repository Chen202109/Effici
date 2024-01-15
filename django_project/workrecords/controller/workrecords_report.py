import copy
import time

from django.shortcuts import render
from django.http import JsonResponse
from mydata import mysql_base
from workrecords.config import constant

from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime
from mydata import mysql_base
from workrecords.services.data_dict_service import encode_data_item, decode_data_item



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


def analysis_select_new(request):
    """
    数据汇报界面的， 新版本的，所选时间段内的出错功能与版本的对比总结表格
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')

        db = mysql_base.Db()

        condition_dict = {
            # error_function是dict 004代表的是问题功能的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_function"],
            "level=": 1
        }
        function_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

        condition_dict = {
            # error_function是dict 004代表的是问题功能的那个数据字典
            "dictCode=": constant.data_dict_code_map["error_type_factor"],
            "level=": 1
        }
        error_factor_list = db.select(["name"], "work_record_data_dict", condition_dict, "")

        # 开始查询生成出错功能和版本对比的表格数据
        sql = f'select softversion, errorfunction, count(*) as amount ' \
              f'from workrecords_2024 where createtime>="{begin_date}" and createtime<="{end_date}" ' \
              f'GROUP BY softversion, errorfunction'
        result = db.select_offset(1, 1000, sql)

        sql = f'select softversion, ' \
              f'count(case when errortypefactor between 10100 and 10200 then 1 else NULL end ) as 产品bug, ' \
              f'count(case when errortypefactor between 10200 and 10300 then 1 else NULL end ) as 异常数据处理, ' \
              f'count(case when errortypefactor between 10300 and 10400 then 1 else NULL end ) as 实施配置, ' \
              f'count(case when errortypefactor between 10400 and 10500 then 1 else NULL end ) as 需求, '\
              f'count(case when errortypefactor between 10500 and 10600 then 1 else NULL end ) as 其他 ' \
              f'from workrecords_2024 where createtime>="{begin_date}" and createtime<="{end_date}" ' \
              f'GROUP BY softversion'
        error_factor_result = db.select_offset(1, 1000, sql)

        data = []
        row_template = {"程序版本": "合计", "受理合计": 0}
        row_template.update({key["name"]:0 for key in function_list})
        row_template.update({key["name"]: 0 for key in error_factor_list})

        if len(result) == 0:
            data.append(row_template)
        else:
            row = copy.deepcopy(row_template)
            sum_row = copy.deepcopy(row_template)
            for i in range(len(result)):
                if row["程序版本"] != result[i]["softversion"]:
                    if i != 0:
                        # 到了不同版本了,添加产品bug等错误因素信息添加，存入数据data，新开一行
                        error_factor_row = next(item for item in error_factor_result if item.get("softversion") == row["程序版本"])
                        # row.update({key["name"]: error_factor_row[key["name"]] for key in error_factor_list})
                        for key in error_factor_list:
                            row.update({key["name"]: error_factor_row[key["name"]]})
                            sum_row.update({key["name"]: sum_row[key["name"]]+error_factor_row[key["name"]]})
                        data.append(row)
                        row = copy.deepcopy(row_template)
                    row["程序版本"] = result[i]["softversion"]
                # 进行对应的版本errorfunction数量添加和合计累计
                row[result[i]["errorfunction"]] += result[i]["amount"]
                row["受理合计"] += result[i]["amount"]
                sum_row[result[i]["errorfunction"]] += result[i]["amount"]
                sum_row["受理合计"] += result[i]["amount"]
            # 最后一行，因为循环到结尾，没有添加，这里添加最后一行version, 然后添加上合计栏
            data.append(row)
            data.append(sum_row)

        return JsonResponse({'status': 200, 'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'status': 405, 'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_problem_type_in_versions_new(request):
    """
    数据汇报界面的， 新版本的，问题分类和各版本和功能的详细对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        party_selected = request.GET.get('partySelected')

        if party_selected =="全部":
            parties = ["财政","行业","第三方"]
        else:
            parties = [party_selected]

        db = mysql_base.Db()

        data = []
        for party in parties:
            party_encoded = encode_data_item(party, constant.data_dict_code_map["error_attribution"])

            condition_dict = {}
            condition_dict["createtime>="] = begin_date
            condition_dict["createtime<="] = end_date
            # 10^3 是因为party的二级现在是3位数，所以是10^3
            condition_dict["belong>="] = party_encoded * 1000
            condition_dict["belong<"] = (party_encoded+1) * 1000
            result = db.select(["errortypefactor", "softversion", "errortype", "count(*) as amount"], "workrecords_2024", condition_dict, "GROUP BY errortypefactor, softversion, errortype")
            print(f"workrecord 2024 table result : {result}")
            version_list = sorted(set(item["softversion"].replace(".", "_") for item in result))

            # 转化成前端可以直接渲染上el-table的形式,格式像这样
            # [{'异常数据处理': '报表功能', 'V3': 1, 'V4_3_1_2': 0, 'V4_3_1_3': 0, 'V4_3_2_0': 2, 'V4_3_2_1': 0}, {...}]
            error_factor_col1_list = {}
            after_time = time.time()
            for item in result:
                # 获取errorfactor大类的decode，如产品bug，实施配置等， errorfactor的码去掉后面两位的小类的编码所以除以100
                error_factor_col1_decoded = decode_data_item(int(item["errortypefactor"]/100), constant.data_dict_code_map["error_type_factor"])
                error_type_decoded = decode_data_item(item["errortype"], constant.data_dict_code_map["error_type"])
                # 因为前端的el-table的表头如果字符串带'.'会失效，转换成"_"传给前端
                version = item["softversion"].replace(".", "_")
                amount = item["amount"]

                # 如果data里面还没有这一项errorfactor大类，添加这一个项目的字典，并且记录下这个在data中的index
                if error_factor_col1_list.get(error_factor_col1_decoded) is None:
                    error_factor_col1_list[error_factor_col1_decoded] = len(data)
                    data.append({
                        "problemParty": party,
                        "problemType": error_factor_col1_decoded,
                        "problemData": []
                    })

                # 从data中找到这一项errorfactor大类对应的问题分类的列表
                problem_data = data[error_factor_col1_list[error_factor_col1_decoded]]["problemData"]
                # 从问题分类的列表去查找当前这个问题的版本字典在列表中的位置，为了后边的添加数据
                problem_data_func_index = None
                for index, error_type_item in enumerate(problem_data):
                    # 如果这个问题分类已经在这个问题因素中登记过，返回这个问题分类所在的位置
                    if error_factor_col1_decoded in error_type_item and error_type_item[error_factor_col1_decoded] == error_type_decoded:
                        problem_data_func_index = index
                # 这个问题分类没有在这个问题因素中登记过，新增一个
                if problem_data_func_index is None:
                    # 放入该问题因素和问题分类的标记，然后放入所有的查询结果的version
                    new_problem_data_func_dict = {error_factor_col1_decoded: error_type_decoded}
                    new_problem_data_func_dict.update({v: 0 for v in version_list})
                    new_problem_data_func_dict["合计"] = amount
                    new_problem_data_func_dict[version] = amount
                    problem_data.append(new_problem_data_func_dict)
                else:
                    # 往版本字典添加
                    problem_data[problem_data_func_index][version] = amount
                    problem_data[problem_data_func_index]["合计"] += amount

        return JsonResponse({'status': 200, 'data': data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'status': 405, 'message': "请求方法错误, 需要GET请求。"})

