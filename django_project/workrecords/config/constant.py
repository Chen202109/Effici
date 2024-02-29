# sql
work_record_col_alias_map = {
    # "fid":"code",
    "belong" : "problemAttribution",
    "recordcode" : "workRecordCode",
    "recordtitle" : "workRecordTitle",
    "creater" : "informer",
    "createtime" : "registerDate",
    "createdirectional" : "informParty",
    "endtime" : "solveDate",
    "problem" : "problemDescription",
    "issolve" : "isSolved",
    "solver" : "solver",
    "solveway" : "solution",
    "reason" : "reasonAnalysis",
    "eventtype" : "eventType",
    "region" : "province",
    "agenname" : "agencyName",
    "agentype" : "productType",
    "environment" : "deployment",
    "errorfunction" : "errorFunction",
    "errortype" : "problemType",
    "errortypefactor":"problemFactor",
    "databasetype" : "DBType",
    "softversion" : "version",
    "jiracode" : "JIRACode",
    "resourcepool" : "sourcePool",
}

work_record_col_chinese_alias_map = {
    "问题归属" : "belong",
    "接入人姓名" : "creater",
    "登记日期" : "createtime",
    "接入方" : "createdirectional",
    "解决日期" : "endtime",
    "问题描述" : "problem",
    "解决" : "issolve",
    "处理人" : "solver",
    "解决方案" : "solveway",
    "原因分析" : "reason",
    "事件" : "eventtype",
    "省份" : "region",
    "单位名称" : "agenname",
    "产品类型" : "agentype",
    "环境属性" : "environment",
    "出错功能" : "errorfunction",
    "问题分类" : "errortype",
    "数据库类型" : "databasetype",
    "程序版本" : "softversion",
    "JIAR编号" : "jiracode",
    "资源池" : "resourcepool",
}

data_dict_code_map = {
    "error_attribution": "001",
    "error_type" : "002",
    "product_type" : "003",
    "error_function" : "004",
    "error_type_factor" : "005",
}

table_chinese_alias_map = {
    "2023工单记录": "workrecords_2023",
    "2024工单记录" : "workrecords_2024",
    "license" : "license_2023",
    "重大故障" : "majorrecords",
    "监控异常" : "monitorrecords",
    "增值服务" : "orderprodct_2023",
    "升级记录" : "upgradeplan_2023",
    "数据字典" : "work_record_data_dict"
}

# error function
work_record_error_function_list = ["开票功能","核销功能","收缴业务","通知交互","报表功能","数据同步","票据管理","license重置","单位开通","增值服务","打印功能","安全漏洞","反算功能"]

saas_service_function_map = {
    'saas-invoice-ebill-server' : '开票功能',
    'saas-billcollection-server': '报表功能',
    'saas-industry-server': '开票功能',
    'saas-finance-adapter-server': '核销功能',
}

saas_function_service_map = {
    "开票功能" : ['saas-invoice-ebill-server', 'saas-invoice-pbill-server', 'saas-industry-server', 'saas-signature-core-server', 'saas-billcollection-server'],
    "收缴业务" : ['saas-paybook-directpaybook-server','saas-paybook-remitpaybook-server'],
    "核销功能" : ['saas-invoice-data-statistical-server', 'saas-bill-collect-server'],
    "打印功能" : [],
    "报表功能" : ['saas-invoice-data-statistical-server', 'saas-industry-report-server'],
    "票据管理" : ['saas-stock-server'],
    "通知交互" : ['saas-notice-server'],
    '数据同步' : ['saas-finance-adapter-server'],
    "安全漏洞" : [],
    "增值服务" : [],
    "单位开通" : [],
    "反算功能" : [],
    "license重置" : [],
}


# map
china_province_list = ['北京','天津','上海','重庆','河北','山西','辽宁','吉林', '云南', '新疆', '广西', '甘肃', '内蒙古', '陕西', '西藏', 
                       '四川', '宁夏', '黑龙江','江苏','浙江','安徽','福建','江西','山东','河南','湖北','湖南','广东','海南', '贵州', '青海', 
                       '台湾', '香港', '澳门']

source_pool_province_map = {
    '01资源池' : ["中央", "宁夏", "贵州", "四川", "山西", "新疆", "福建", "北京"],
    '03资源池' : ["广西", "内蒙古", "湖北", "云南", "陕西", "天津", "广东", "深圳"],
    '04资源池' : ["甘肃", "青岛", "海南", "黑龙江", "辽宁", "西藏", "重庆", "吉林", "山东"],
}

province_source_pool_map = {
    "中央" : "01资源池",
    "宁夏" : "01资源池",
    "贵州" : "01资源池",
    "四川" : "01资源池",
    "山西" : "01资源池",
    "新疆" : "01资源池",
    "福建" : "01资源池",
    "北京" : "01资源池",

    "广西": "03资源池",
    "内蒙古": "03资源池",
    "湖北": "03资源池",
    "云南": "03资源池",
    "陕西": "03资源池",
    "天津": "03资源池",
    "广东": "03资源池",
    "深圳": "03资源池",

    "甘肃": "04资源池",
    "青岛": "04资源池",
    "海南": "04资源池",
    "黑龙江": "04资源池",
    "辽宁": "04资源池",
    "西藏": "04资源池",
    "重庆": "04资源池",
    "吉林": "04资源池",
    "山东": "04资源池",
}


#path
# 开发环境下的配置
MEDIA_ROOT = r"E:\myWork\Effici\django_project\media_files\workrecords"
AGENCY_ACCOUNT_FILE_ROOT = './workrecords/config/agency_account/'

# 生产环境下的路径配置
# import os
# BACKEND_CODE_DIR = os.environ.get('backendCodeDir')
# MEDIA_ROOT = os.path.join(BACKEND_CODE_DIR, 'media_files/workrecords/')
# AGENCY_ACCOUNT_FILE_ROOT = os.path.join(BACKEND_CODE_DIR, 'workrecords/config/agency_account/')

