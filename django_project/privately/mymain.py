from myoffice import excel_workrecord
from myoffice import excel_license
from myoffice import excel_upgrade
from myoffice import excel_majorrecord
from myoffice import excel_any
from mydata import mysql_base


def workrecord_import(excelfilePath):
    sql_key_str,sql_value_list = excel_workrecord.workrecord_inster_sql(excelfilePath)
    # print(sql_key_str)
    # for s in range(len(sql_value_list)):
    #     print(sql_value_list[s])

    return sql_key_str,sql_value_list

def license_import(excelfilePath):
    sql_key_str,sql_value_list = excel_license.license_inster_sql(excelfilePath)
    # print(sql_key_str)
    # for s in range(len(sql_value_list)):
    #     print(sql_value_list[s])

    return sql_key_str,sql_value_list

def upgrade_import(excelfilePath):
    sql_key_str,sql_value_list = excel_upgrade.upgrade_inster_sql(excelfilePath)
    # print(sql_key_str)
    # for s in range(len(sql_value_list)):
    #     print(sql_value_list[s])

    return sql_key_str,sql_value_list

def majorrecord_import(excelfilePath):
    sql_key_str,sql_value_list = excel_majorrecord.majorrecor_inster_sql(excelfilePath)
    # print(sql_key_str)
    # for s in range(len(sql_value_list)):
    #     print(sql_value_list[s])

    return sql_key_str,sql_value_list

def any_import(excelfilePath,excelnameField,data_title,sql_key_head='',sql_value_head=''):
    sql_key_str,sql_value_list = excel_any.any_inster_sql(excelfilePath,excelnameField,data_title,sql_key_head,sql_value_head)
    # print(sql_key_str)
    # for s in range(len(sql_value_list)):
    #     print(sql_value_list[s])  file_path,name_field

    return sql_key_str,sql_value_list

if __name__ == '__main__':
    # 导入受理数据的 excel
    # file_path = f'C:\\Users\\Administrator\\Downloads\\受理数据导入文件.xlsx'
    # sql_key_str,sql_value_list = workrecord_import(file_path)
    # db = mysql_base.Db()
    # for i in range(len(sql_value_list)):
    #     result = db.insert('workrecords_2023',sql_key_str,sql_value_list[i])
    #     print(f'插入第{i+1}行数据，返回 {result}')

    # # 导入license 数据的 excel
    # file_path = f'C:\\Users\\Administrator\\Downloads\\license数据导入文件.xlsx'
    # sql_key_str,sql_value_list = license_import(file_path)
    # db = mysql_base.Db()
    # for i in range(len(sql_value_list)):
    #     result = db.insert('license_2023',sql_key_str,sql_value_list[i])
    #     print(f'插入第{i}次数据，返回 {result}')

    # # 导入升级计划 数据的 excel
    # file_path = f'C:\\Users\\Administrator\\Downloads\\升级计划导入文件.xlsx'
    # sql_key_str,sql_value_list = upgrade_import(file_path)
    # db = mysql_base.Db()
    # for i in range(len(sql_value_list)):
    #     result = db.insert('upgradeplan_2023',sql_key_str,sql_value_list[i])
    #     print(f'插入第{i}次数据，返回 {result}')

    # # 导入重大故障 数据的 excel
    # file_path = f'C:\\Users\\Administrator\\Downloads\\重大故障导入文件.xlsx'
    # sql_key_str,sql_value_list = majorrecord_import(file_path)
    # db = mysql_base.Db()
    # for i in range(len(sql_value_list)):
    #     result = db.insert('majorrecords',sql_key_str,sql_value_list[i])
    #     print(f'插入第{i}次数据，返回 {result}')

    # 导入监控异常 数据的 excel
    # file_path = f'C:\\Users\\Administrator\\Downloads\\监控异常导入文件.xlsx'
    # name_field = {
    #     '是否解决':'issolve','省份':'region','接入人':'creater','问题归属':'belong','项目名称':'agenname','资源池':'resourcepool',
    #     '异常分类':'errortype','事项详情': 'problem','事项开始时间':'createtime','事项线束时间':'endtime','事项处理人':'solver',
    #     '处理方案':'solveway'
    # }
    #
    # sql_key_str,sql_value_list = any_import(file_path,name_field)
    # db = mysql_base.Db()
    # for i in range(len(sql_value_list)):
    #     result = db.insert('monitorrecords',sql_key_str,sql_value_list[i])
    #     print(f'插入第{i}次数据，返回 {result}')

    # 导入 增值服务开通结果 excel
    file_path = f'C:\\Users\\Administrator\\Downloads\\增值服务导入文件.xlsx'
    name_field = {
        '省份':'region','产品名称':'ordername','财政编码':'regioncode','区划编码':'areacode','单位名称':'agenname','开通日期':'createtime'
    }
    data_title = '日期'
    sql_key_str,sql_value_list = any_import(file_path,name_field,data_title)
    db = mysql_base.Db()
    for i in range(len(sql_value_list)):
        result = db.insert('orderprodct_2023',sql_key_str,sql_value_list[i])
        print(f'插入第{i}次数据，返回 {result}')


    # 查询受理数据的部分
    # db = mysql_base.Db()
    # sql = 'select count(1) as value, errorfunction from workrecords_2023 GROUP BY errorfunction'
    # results=db.select_offset(1,1000,sql)
    # print(type(results),len(results))
    # print(results)