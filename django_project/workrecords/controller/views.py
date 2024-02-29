from django.http import JsonResponse
from datetime import datetime,timedelta # 用于传入的字符串转换成日期 datetime.strptime
from mydata import mysql_base
from workrecords.exception.service.EfficiServiceException import EfficiServiceException

# ----------------------------------------------------------- AnalysisLargeProblemData.vue 的请求 --------------------------------------------

def get_saas_large_problem_province_list(request):
    """
    获取私有化重大问题的省份
    """
    if request.method == 'GET':
        try:
            db = mysql_base.Db()
            saas_large_problem_province_list = db.select(["distinct region"], "majorrecords", {}, "")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={'seriesName': "重大故障省份", 'seriesData': saas_large_problem_province_list}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_large_problem_by_type_and_province(request):
    """
    分析私有化重大故障的出错功能和省份的对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='')
        end_date = request.GET.get('endData',default='')
        province = request.GET.get('provinceSelected', default='')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        try:
            db = mysql_base.Db()
            condition_dict = {"createtime>=": str(real_date_begin), "createtime<=":str(real_date_end), "region=":province}
            result = db.select(["errortype as x", "count(*) as y"], "majorrecords", condition_dict, "group by x")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        data = [{'seriesName': province+"重大问题分类", 'seriesData': result}]
        return JsonResponse(status=200, data={"data":data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_large_problem_by_province(request):
    """
    分析私有化重大故障的问题数量的省份对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData')
        end_date = request.GET.get('endData')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        try:
            db = mysql_base.Db()
            # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]
            condition_dict = {"createtime>=": str(real_date_begin), "createtime<=": str(real_date_end)}
            result = db.select(["region as x", "count(*) as y"], "majorrecords", condition_dict, "group by x")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        data = [{'seriesName': "问题受理数量", 'seriesData': result}]
        return JsonResponse(status=200, data={"data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_large_problem_by_type(request):
    """
    分析出现的重大生产故障的问题分类
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        db =mysql_base.Db()
        data = []

        # 查询这段时间内的线上重大故障，将他们count一遍然后生成和上面一样的格式append到data中
        sql = f' SELECT errortype as name, count(*) as value from majorrecords WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" group by name'
        saas_large_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "私有化重大故障问题分类", 'seriesData': saas_large_problem_data})

        # 进行排序，找出top10, 并且加上总数
        total = sum(item['value'] for item in saas_large_problem_data)
        sorted_data = sorted(saas_large_problem_data, key=lambda x : x['value'], reverse = True)[0:10]
        for item in sorted_data: item['percent'] = f"{((item['value'] / total) * 100):.2f}%" if total!=0 else 0
        data.append({'seriesName': "私有化重大故障top10", 'seriesData': sorted_data})
        data.append({'seriesName': "私有化重大故障数量合计", 'seriesData': [{"name":"合计", "value":total, "percent":""}]})

        return JsonResponse(status=200, data={"data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

# ----------------------------------------------------------- AnalysisLargeProblemData.vue 的请求 --------------------------------------------

# ----------------------------------------------------------- AnalysisMonitorProblem.vue 的请求 --------------------------------------------

def get_saas_monitor_province_list(request):
    """
    获取监控异常这边的省份
    """
    if request.method == 'GET':
        try:
            db = mysql_base.Db()
            result = db.select(["distinct region"], "monitorrecords", {}, "")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={'seriesName': "监控出错省份", 'seriesData': result}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_monitor_problem_by_type_and_province(request):
    """
    分析生产环境监控异常的出错功能和省份的对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='')
        end_date = request.GET.get('endData', default='')
        province = request.GET.get('provinceSelected', default='')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        try:
            db = mysql_base.Db()
            condition_dict = {"createtime>=": str(real_date_begin), "createtime<=":str(real_date_end), "region=":province}
            result = db.select(["errortype as x", "count(*) as y"], "monitorrecords", condition_dict, "group by x")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={'data': [{'seriesName': province + "监控出错功能", 'seriesData': result}]},
                            json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_monitor_problem_by_province(request):
    """
    分析生产环境监控异常的问题数量的省份对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData',default='')
        end_date = request.GET.get('endData',default='')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        try:
            db = mysql_base.Db()
            # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]
            condition_dict = {"createtime>=": str(real_date_begin), "createtime<=": str(real_date_end)}
            result = db.select(["region as x", "count(*) as y"], "monitorrecords", condition_dict, "group by x")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        data = [{'seriesName': "问题受理数量", 'seriesData': result}]
        return JsonResponse(status=200, data={"data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_minitor_problem_by_type(request):
    """
    分析省份出现的重大生产故障的数量
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='')
        end_date = request.GET.get('endData', default='')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        data = []
        db =mysql_base.Db()
        sql = f' SELECT errortype as name, count(*) as value from monitorrecords WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" group by name'
        saas_monitor_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "生产监控异常问题分类", 'seriesData': saas_monitor_problem_data})

        # 进行排序，找出top10, 并且加上总数
        total = sum(item['value'] for item in saas_monitor_problem_data)
        sorted_data = sorted(saas_monitor_problem_data, key=lambda x : x['value'], reverse = True)[0:10]
        for item in sorted_data: item['percent'] = f"{((item['value'] / total) * 100):.2f}%" if total!=0 else 0
        data.append({'seriesName': "生产监控异常问题top10", 'seriesData': sorted_data})
        data.append({'seriesName': "生产监控异常问题合计", 'seriesData': [{"name":"合计", "value":total, "percent":""}]})
        
        return JsonResponse(status=200, data={"data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

# ----------------------------------------------------------- AnalysisMonitorProblem.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisAddedServiceData.vue 的请求 --------------------------------------------

def get_saas_added_service_province_list(request):
    """
    获取增值服务这边的省份
    """
    if request.method == 'GET':
        try:
            db = mysql_base.Db()
            result = db.select(["distinct region"], "orderprodct_2023", {}, "")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})
        return JsonResponse(status=200, data={'seriesName': "订购增值产品省份", 'seriesData': result}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_added_service_by_type_and_province(request):
    """
    分析增值服务订购的的服务类别和省份的对比
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='')
        end_date = request.GET.get('endData',default='')
        province = request.GET.get('provinceSelected', default='')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        try:
            db = mysql_base.Db()
            condition_dict = {"createtime>=": str(real_date_begin), "createtime<=":str(real_date_end), "region=":province}
            result = db.select(["ordername as x", "count(*) as y"], "orderprodct_2023", condition_dict, "group by x")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        data = [{'seriesName': province+"增值服务类别", 'seriesData': result}]
        return JsonResponse(status=200, data={"data":data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_added_service_by_province(request):
    """
    分析增值服务开通的省份对比。
    """
    if request.method == 'GET':
        begin_date = request.GET.get('beginData',default='')
        end_date = request.GET.get('endData',default='')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        try:
            db = mysql_base.Db()
            # 查询数据库的所有region并放入数组中，数组格式为[{"x":"省份名称","y":受理问题的数量}]
            condition_dict = {"createtime>=": str(real_date_begin), "createtime<=": str(real_date_end)}
            result = db.select(["region as x", "count(*) as y"], "orderprodct_2023", condition_dict, "group by x")
        except EfficiServiceException as e:
            return JsonResponse(status=e.status, data={'message': e.msg})

        data = [{'seriesName': "增值服务开通数量", 'seriesData': result}]
        return JsonResponse(status=200, data={"data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})


def analysis_saas_added_service_by_type(request):
    """
    分析增值服务的服务分类对比
    """

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')
        real_date_begin = datetime.strptime(begin_date, '%Y-%m-%d')
        real_date_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        data = []
        db =mysql_base.Db()
        sql = f' SELECT ordername as name, count(*) as value from orderprodct_2023 WHERE createtime >= "{real_date_begin}" AND createtime <= "{real_date_end}" group by name'
        saas_monitor_problem_data = db.select_offset(1, 2000, sql)
        data.append({'seriesName': "增值服务分类", 'seriesData': saas_monitor_problem_data})

        # 进行排序，找出top10, 并且加上总数
        total = sum(item['value'] for item in saas_monitor_problem_data)
        sorted_data = sorted(saas_monitor_problem_data, key=lambda x : x['value'], reverse = True)[0:10]
        for item in sorted_data: item['percent'] = f"{((item['value'] / total) * 100):.2f}%" if total!=0 else 0
        data.append({'seriesName': "增值服务top10", 'seriesData': sorted_data})
        data.append({'seriesName': "增值服务合计", 'seriesData': [{"name":"合计", "value":total, "percent":""}]})

        return JsonResponse(status=200, data={"data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

# ----------------------------------------------------------- AnalysisAddedServiceData.vue 的请求 --------------------------------------------


# ----------------------------------------------------------- AnalysisPrivatizationLicense.vue 的请求 --------------------------------------------

def analysis_saas_privatization_license_register_province(request):
    """
    分析私有化license开通数量的省份的数据
    """

    if request.method == 'GET':
        begin_date = request.GET.get('beginData', default='2023-01-01')
        end_date = request.GET.get('endData', default='2023-12-31')

        try:
            db = mysql_base.Db()
            sql = f'select DISTINCT region,COUNT(DISTINCT agenname) as count from license_2023 where authorizeddate>="{begin_date}" and authorizeddate<="{end_date}" GROUP BY region ORDER BY count desc'
            license_register_province_data = db.select_offset(1, 1000, sql)
            # 这个是查询后返回的数据，类似 [{'region': '上海', 'count': 2}, {'region': '北京', 'count': 1}]
            # 将上面的转成下面这种，这样前端才能挂到license_data里面
            # [{'上海': 2, '北京':3, '广东':3}]
            # 生成要转化成的数据类型, 并加入表头表尾
            license_data = [{"省份": "单位申请数"}]
            sum_license_register = 0
            for item in license_register_province_data:
                sum_license_register += item["count"]
                license_data.append({item["region"]: item["count"]})
            license_data.append({"合计": sum_license_register})
            data = {'seriesName': "v4 license受理数据统计", 'seriesData': license_data}
        except Exception as e:
            # return JsonResponse(status=e.status, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})
            return JsonResponse(status=400, data={'message': str(e)}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(status=200, data=data, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(status=405, data={'message': "请求方法错误, 需要GET请求。"})

# ----------------------------------------------------------- AnalysisPrivatizationLicense.vue 的请求 --------------------------------------------

if __name__ == '__main__':
    pass