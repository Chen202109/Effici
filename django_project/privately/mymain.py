from myoffice import excel_workrecord
from myoffice import excel_license
from myoffice import excel_upgrade
from mydata import mysql_base

def workrecord_import(excelfilePath):
    sql_key_str,sql_value_list = excel_workrecord.workrecord_inster_sql(excelfilePath)
    print(sql_key_str)
    for s in range(len(sql_value_list)):
        print(sql_value_list[s])

    return sql_key_str,sql_value_list

def license_import(excelfilePath):
    sql_key_str,sql_value_list = excel_license.license_inster_sql(excelfilePath)
    print(sql_key_str)
    for s in range(len(sql_value_list)):
        print(sql_value_list[s])

    return sql_key_str,sql_value_list

def upgrade_import(excelfilePath):
    sql_key_str,sql_value_list = excel_upgrade.upgrade_inster_sql(excelfilePath)
    print(sql_key_str)
    for s in range(len(sql_value_list)):
        print(sql_value_list[s])

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
    file_path = f'C:\\Users\\Administrator\\Downloads\\license数据导入文件.xlsx'
    sql_key_str,sql_value_list = license_import(file_path)
    db = mysql_base.Db()
    for i in range(len(sql_value_list)):
        result = db.insert('license_2023',sql_key_str,sql_value_list[i])
        print(f'插入第{i}次数据，返回 {result}')

    # # 导入升级计划 数据的 excel
    # file_path = f'C:\\Users\\Administrator\\Downloads\\升级计划导入文件.xlsx'
    # sql_key_str,sql_value_list = upgrade_import(file_path)
    # db = mysql_base.Db()
    # for i in range(len(sql_value_list)):
    #     result = db.insert('upgradeplan_2023',sql_key_str,sql_value_list[i])
    #     print(f'插入第{i}次数据，返回 {result}')

    # 查询受理数据的部分
    # db = mysql_base.Db()
    # sql = 'select count(1) as value, errorfunction from workrecords_2023 GROUP BY errorfunction'
    # results=db.select_offset(1,1000,sql)
    # print(type(results),len(results))
    # print(results)