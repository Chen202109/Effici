
from django.shortcuts import render
from django.http import JsonResponse
from mydata import mysql_base
from collections import Counter
from workrecords.config import constant

from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime

from mydata import mysql_base
import pandas as pd

def analysis_saas_problem_by_country(request):
    """
    分析每个省份的数据，给全国地图使用
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        db =mysql_base.Db()

        # 查询数据库的workrecord表然后所有region并放入数组中
        sql = f' SELECT distinct region as name, count(*) as value from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" group by region '
        saas_province_problem_data = db.select_offset(1, 2000, sql)

        # 对上线单位数量统计进行读取, 因为是地图，所以把key给改成name和value, 而不是柱状图的x和y
        saas_province_agency_account_data = pd.read_csv(constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_by_year_2023.csv",sep=',').rename(columns={'省份':'name','数量':'value'}).to_dict(orient="records")

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
            saas_country_data.append({'name':prov, 'value': value, 'agencyValue': agency_value})
        data.append({'seriesName': "全国"+"受理数量", 'seriesData': saas_country_data})
        data.append({"valueMax": value_max})
        
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_problem_by_country_region(request):
    """
    分析每个省份的数据统计，给全国地图周围的几张表使用
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        province = request.GET.get('province', default='全国')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()
        province_condition_sql = "" if province=='全国' else f' AND region = "{province}" '

        # 对出错问题（开票，核销，数据同步等）进行统计Top5
        sql = f' SELECT distinct errorfunction as x, count(*) as y from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} group by errorfunction '
        saas_function_type_data = db.select_offset(1, 2000, sql)
        # 排序并找出前五
        sorted_saas_function_type_data = sorted(saas_function_type_data, key=lambda x : x['y'], reverse = True)[0:5]
        function_type_bar_gragh = []
        function_type_bar_gragh.append({'seriesName': province+"出错功能Top5", 'seriesData': sorted_saas_function_type_data})
        data.append(function_type_bar_gragh)

        # 对问题分类（实施配置，异常数据处理等）进行统计排序
        sql = f' SELECT distinct errorType as x, count(*) as y from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} group by errorType '
        saas_problem_type_data = db.select_offset(1, 2000, sql)
        # 排序并找出前五
        sorted_saas_problem_type_data = sorted(saas_problem_type_data, key=lambda x : x['y'], reverse = True)[0:5]
        problem_type_bar_gragh = []
        problem_type_bar_gragh.append({'seriesName': province+"问题分类Top5", 'seriesData': sorted_saas_problem_type_data})
        data.append(problem_type_bar_gragh)

        # 对生产监控异常的数据进行统计排序
        sql = f' SELECT distinct errorType as x, count(*) as y from monitorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" {province_condition_sql} group by errorType '
        saas_monitor_problem_type_data = db.select_offset(1, 2000, sql)
        # 排序并找出前五, 因为前端使用横向柱状图，所以排序要反着来
        sorted_saas_monitor_problem_type_data = sorted(saas_monitor_problem_type_data, key=lambda x : x['y'], reverse = False)[-5:]
        monitor_problem_type_bar_gragh = []
        monitor_problem_type_bar_gragh.append({'seriesName': province+"生产监控问题分类Top5", 'seriesData': sorted_saas_monitor_problem_type_data})
        data.append(monitor_problem_type_bar_gragh)

        # 对版本号和受理进行查询
        sql = f' SELECT distinct softversion as x, errorfunction, count(*) as y from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} group by softversion, errorfunction '
        saas_soft_version_data = db.select_offset(1, 2000, sql)

        # 因为前端想要tooltip展示每个版本号出错功能的前三，所以在这里进行每个版本出错功能的排序
        series_data = []
        curr_version = 0
        version_amount = 0
        version_function_list = []
        for i in range(len(saas_soft_version_data)):

            if (curr_version != 0 and curr_version != saas_soft_version_data[i]['x']):
                # 说明要换成下个月的数据了，所以将当前存储的当前月份的数据进行出错功能的排序取前五和添加到series_data中
                version_function_list.sort(key=lambda x: x['amount'], reverse=True)
                series_data.append({'x': curr_version, 'y':version_amount, 'functionType' : version_function_list[0:3]})
                # 将临时数据进行清空
                version_amount = 0
                version_function_list = []

            # 还在当前月份，那么就往临时数据里面添加当前月份的出错功能和累加出错的量
            curr_version = saas_soft_version_data[i]['x']    
            version_amount += saas_soft_version_data[i]['y']
            version_function_list.append({"function": saas_soft_version_data[i]['errorfunction'], 'amount' : saas_soft_version_data[i]['y']})
            
            if (i== len(saas_soft_version_data)-1):
                # 说明所有数据查到最后一项了，该要退出循环了，将这个月份的数据加入series_data中
                version_function_list.sort(key=lambda x: x['amount'], reverse=True)
                series_data.append({'x': curr_version, 'y':version_amount, 'functionType' : version_function_list[0:3]})

        soft_version_amount_bar_gragh = []
        soft_version_amount_bar_gragh.append({'seriesName': province+"版本受理统计", 'seriesData': series_data})
        data.append(soft_version_amount_bar_gragh)


        # 对产品分类（医疗，通用，高校等）进行统计
        sql = f' SELECT distinct agentype as name, count(*) as value from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} group by agentype '
        saas_agency_type_data = db.select_offset(1, 2000, sql)
        agency_type_pie_gragh = []
        agency_type_pie_gragh.append({'seriesName': province+"受理行业种类", 'seriesData': saas_agency_type_data})
        data.append(agency_type_pie_gragh)

        # 对重大故障的问题分类进行统计排序
        sql = f' SELECT distinct errorType as x, count(*) as y from majorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" {province_condition_sql} group by errorType '
        saas_large_problem_type_data = db.select_offset(1, 2000, sql)
        # 排序并找出前五, 这里reverse为false是因为前端使用的是横向的柱状图，他会把排序完的第一个的放在最底下，想要数值高的放在上方，reverse为false
        sorted_saas_large_problem_type_data = sorted(saas_large_problem_type_data, key=lambda x : x['y'], reverse = False)[-5:]
        large_problem_type_bar_gragh = []
        large_problem_type_bar_gragh.append({'seriesName': province+"私有化重大故障问题分类Top5", 'seriesData': sorted_saas_large_problem_type_data})
        data.append(large_problem_type_bar_gragh)

        # 对合计的数据进行统计添加
        sql = f'SELECT "受理问题合计" as name, count(*) as value from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} '\
              f'UNION ALL '\
              f'SELECT "V4 license受理合计" as name, count(*) from license_2023 WHERE authorizeddate >= "{begin_date}" AND authorizeddate <= "{end_date}" {province_condition_sql} '\
              f'UNION ALL '\
              f'select "私有化重大故障合计" as name, count(*) from majorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" {province_condition_sql} '\
              f'UNION ALL '\
              f'select "生产监控问题合计" as name, count(*) from monitorrecords WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" {province_condition_sql} '\
              f'UNION ALL '\
              f'select "增值服务开通合计" as name, count(*) from orderprodct_2023 WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" {province_condition_sql} '
        saas_country_summary_table_data = db.select_offset(1, 2000, sql)

        # 上线单位数量统计, 因为是跨越时间的查询，查询这段时间内的单位新增
        begin_time_year = int(begin_date.split("-")[0])
        begin_time_month = int(begin_date.split("-")[1])
        end_time_year = int(end_date.split("-")[0])
        end_time_month = int(end_date.split("-")[1])
        agency_amount = 0
        while (begin_time_year <= end_time_year):
            # 打开该年的csv, 因为现在只有2020-2023,其他年份的会找不到报错
            try:
                dataframe = pd.read_csv(f"{constant.AGENCY_ACCOUNT_FILE_ROOT}agency_account_increment_{begin_time_year}.csv",sep=',', index_col = 0)
            except FileNotFoundError:
                begin_time_year += 1
                continue
            if (begin_time_year == end_time_year):
                while (True):
                    agency_amount += int(dataframe.loc[province,str(begin_time_month)+'月'])
                    if begin_time_month == end_time_month:
                        break
                    begin_time_month += 1
                break
            else:
                while (begin_time_month <= 12):
                    agency_amount += int(dataframe.loc[province,str(begin_time_month)+'月'])
                    begin_time_month += 1
                begin_time_month = 1
                begin_time_year += 1
        # 对上线单位数量统计进行读取和插入到summary table中
        saas_country_summary_table_data.insert(0, { "name":'上线单位合计', "value" : agency_amount })

        saas_country_summary_table = []
        saas_country_summary_table.append({'seriesName': province+"合计数据", 'seriesData': saas_country_summary_table_data})
        data.append(saas_country_summary_table)
        
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_saas_function_by_province(request):
    """
    分析省份受理的功能的问题数量的对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        function_name = request.GET.get('functionName').split(',')

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

        # 对上线单位数量统计进行读取
        dataframe = pd.read_csv(constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_by_year_2023.csv",sep=',').rename(columns={'省份':'x','数量':'y'}).to_dict(orient="records")
        # 生成一个顺序与saas_province_problem_data一致的数组，目的是为了两条series数据里面相同位置的字典对应的x值一致，那样抽取的y的值才一致。
        # 新数组的x值通过saas_province_problem_data获取，y的值通过dataFrame读取的上线单位的数量进行填入。
        # 如果是这一行报错StopIteration，基本上就是登记的时候省份没有登记对，比如内蒙古写成内蒙，需要去数据库进行调整让省份和constant.AGENCY_ACCOUNT_FILE_ROOT+"agency_account_by_year_2023.csv"的省份名称一致
        saas_province_agency_account_data = [{**prov, 'y': next(filter(lambda ag: ag['x'] == prov['x'], dataframe))['y']} for prov in saas_province_problem_data]
        data.append({'seriesName': "上线单位数量", 'seriesData': saas_province_agency_account_data})
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})


def analysis_version_upgrade_trend(request):
    """
    分析版本信息和bug的趋势对比。
    """
    data = []

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        function_name = request.GET.get('functionName').split(',')
        province = request.GET.get('provinceSelected')

        realdate_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        realdate_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()

        province_condition_sql = "" if province=='全国' else f' AND region = "{province}" '

        sql = f'SELECT DISTINCT softversion as x from workrecords_2023 WHERE createtime >= "{begin_date}" AND createtime <= "{end_date}" {province_condition_sql} ORDER BY softversion '
        saas_version_data = db.select_offset(1, 2000, sql)

        for i in range(len(function_name)):
            sql = f' SELECT softversion as x, COUNT(*) as y from workrecords_2023 '\
                  f' WHERE createtime >= "{realdate_begin}" AND createtime <= "{realdate_end}" '\
                  f' {province_condition_sql} ' \
                  f' AND errorfunction = "{function_name[i]}" ' \
                  f' GROUP BY softversion'
            saas_function_data = db.select_offset(1, 2000, sql)
            saas_version_data = [{'x': entry['x'], 'y': next((value['y'] for value in saas_function_data if value['x'] == entry['x']), 0)} for entry in saas_version_data]
            data.append({'seriesName': function_name[i], 'seriesData': saas_version_data})
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
        sql = f' SELECT MONTH(createtime) AS Month, errorfunction, COUNT(*) AS ProblemAmount '\
              f' FROM workrecords_2023 '\
              f' WHERE MONTH(createtime) between {datetime.strptime(begin_date, "%Y-%m-%d").month} AND {datetime.strptime(end_date, "%Y-%m-%d").month} '\
              f' GROUP BY MONTH(createtime), errorfunction'
        saas_month_data = db.select_offset(1, 2000, sql)

        # 因为前端想要tooltip展示每个月出错功能的前五，所以在这里进行每个月出错功能的排序
        series_data = []
        curr_month = 0
        month_amount = 0
        month_function_list = []
        for i in range(len(saas_month_data)):
            if (curr_month != 0 and curr_month != saas_month_data[i]['Month']) or (i== len(saas_month_data)-1):
                # 说明要换成下个月的数据了，或者是已经到查询的月份的末尾了，所以将当前存储的当前月份的数据进行出错功能的排序取前五和添加到series_data中
                month_function_list.sort(key=lambda x: x['amount'], reverse=True)
                series_data.append({'x':str(curr_month)+'月', 'y':month_amount, 'functionType' : month_function_list[0:5]})
                # 将临时数据进行清空
                month_amount = 0
                month_function_list = []
            # 还在当前月份，那么就往临时数据里面添加当前月份的出错功能和累加出错的量
            curr_month = saas_month_data[i]['Month']    
            month_amount += saas_month_data[i]['ProblemAmount']
            month_function_list.append({"function": saas_month_data[i]['errorfunction'], 'amount' : saas_month_data[i]['ProblemAmount']})

        data.append({'seriesName': "问题受理数量", 'seriesData': series_data})
            
    return JsonResponse({'data': data}, json_dumps_params={'ensure_ascii': False})
