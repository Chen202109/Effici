from workrecords.exception.dao.MyConnectionException import MyConnectionException
from workrecords.exception.dao.EfficiDaoException import EfficiDaoException
import json
import pymysql
import pandas as pd

class Db(object):
    def __init__(self):
        try:
            self.configure = pymysql.connect(
                host='172.18.150.4',
                port=3306,
                database='saasoperation',
                charset='utf8',
                user='root',
                passwd='admin'
            )
            self.begin = self.configure.cursor(pymysql.cursors.DictCursor)
        except pymysql.err.OperationalError:
            raise MyConnectionException("未能连接数据库, 可能数据库连接参数有误。")
        except pymysql.err.InternalError:
            raise MyConnectionException("未能连接数据库, 可能python版本、python引用数据库的引擎版本与Mysql服务端版本不相匹配。")

    # select查询语句
    def select(self,field: list, table: str, where: dict = None, other: str = ""):
        """
        :param field: 需要查询的字段名称 [str, str, ...]
        :param table: 表名，如需多表联查请在表名后面加上 => "table_name as `c` inner join table_name as b ..."
        :param where: 查询条件，非必填 => {"name =": "alex", " OR title like": "'%{}%'".format(title), ...}
        :param other: 其他跟在where后面的条件
        :return: ({"key": "value", ...} ...)
        """
        _field = ",".join(field)
        if where:
            where_str = ""
            for key, value in where.items():
                if value is None or value == "" or value == "None":
                    continue
                elif type(value) == int:
                    value = value
                    where_str += " AND " + "%s" % key + " " + "%d" % value
                elif type(value) == float:
                    value = value
                    where_str += " AND " + "%s" % key + " " + "%f" % value
                else:
                    print(f"ddd: {value}")
                    value = value.replace("'", '"')
                    where_str += " AND " + "%s" % key + " " + "'%s'" % value
            if where_str == "":
                sql = "SELECT " + _field + " FROM " + table + " %s " % other
            else:
                sql = "SELECT " + _field + " FROM " + table + " WHERE" + " 1 = 1 " + where_str + " %s " % other
        else:
            sql = "SELECT " + _field + " FROM " + table + " %s " % other
        try:
            print(f"select sql is : {sql}")
            self.configure.ping(reconnect=True)
            self.begin.execute(sql)
            self.configure.commit()
            results = self.begin.fetchall()

            if len(field) == 1 and field[0] != "*":
                try:
                    if len(results) == 1:
                        return results[0][field[0]]
                except IndexError:
                    print("询数据为空 SQL statement: ", sql)  # 打印SQL语句
                except KeyError:
                    print("使用别名查询")
                    return results

            return results
        except pymysql.err.ProgrammingError as error:
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.InternalError as error:
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.OperationalError as error:
            self.configure.close()
            raise MyConnectionException("未能连接数据库。")

    # 分页方式查询
    # def select_offset(self, page, page_size,table,final_key,final_where,other):
    def select_offset(self, page, page_size, sql):
        #sql = "SELECT " + final_key + " FROM " + table + " WHERE" + " 1 = 1 AND" + final_where + " %s " % other
        #这里page 表示页，第几页；通过例如第5页每页10行，则 page=49
        page = (page - 1) * page_size
        #例如通过计算后page=49，page_size=10, 表示从第50行开始，检索10行记录，即：检索记录行50-60，
        sql = sql + ' limit '+ str(page) +' ,'+str(page_size)  # mysql没有 execute(sql, offset) ,所以是通过limit 来分页

        print(sql)
        try:
            self.configure.ping(reconnect=True)
            self.begin.execute(sql)
            self.configure.commit()
            results = self.begin.fetchall()
            # 返回的是个list, 像这样 [{},{},{}]
            return results

        except pymysql.err.ProgrammingError as error:
            self.configure.close()
            return error
        except pymysql.err.InternalError as error:
            self.configure.close()
            return error
        except pymysql.err.OperationalError as error:
            self.configure.close()
            return error

    # insert语句
    # INSERT INTO table_name (列1, 列2,...) VALUES (值1, 值2,....)
    def insert(self,table,final_key,final_value):
        sql = "INSERT INTO " + table + " (" + final_key + ")" + " VALUES (" + final_value + ")"
        # print(f'即将执行sql为{sql}')
        try:
            self.configure.ping(reconnect=True)
            self.begin.execute(sql)
            self.configure.commit()
        except pymysql.err.ProgrammingError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.InternalError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.OperationalError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.InterfaceError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.DataError as error:
            self.configure.rollback()
            self.configure.close()
            return error


    # insert语句
    # INSERT INTO table_name (列1, 列2,...) VALUES (值1, 值2,....)
    def insert_copy(self, table, field: dict):
        """
        :param table: 表名
        :param field: {字段名称 => str：值 => str, ...}
        :return: 只有异常才有返回值
        """
        key_list = []
        value_list = []
        for field_key, field_value in field.items():
            key = str(field_key)
            if type(field_value) == dict:
                value = json.dumps(field_value)
                value = value.replace("\\", '\\\\')
                value = value.replace("'", '\\\\"')
            elif type(field_value) == int:
                value = field_value
            elif type(field_value) == float:
                value = field_value
            elif field_value is None:
                value = field_value
            else:
                value = str(field_value)
                value = value.replace("'", '"')
            key_list.append(key)
            value_list.append(value)

        final_key = ','.join(key_list)
        final_value = str(value_list)[1:-1]

        sql = "INSERT INTO " + table + " (" + final_key + ")" + " VALUES (" + final_value + ")"
        # 因为python中是没有null，而且这里好像不能自动转换，所以在语句中进行转换。
        sql = sql.replace("None", "Null")
        try:
            self.configure.ping(reconnect=True)
            print(f"Insert sql is: {sql}")
            result = self.begin.execute(sql)
            self.configure.commit()
        except pymysql.err.ProgrammingError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.InternalError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.OperationalError as error:
            self.configure.rollback()
            self.configure.close()
            raise MyConnectionException("未能连接数据库。")
        except pymysql.err.InterfaceError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.DataError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))

    # insert 语句
    # 批量插入
    def group_insert_dataframe(self, table_name, df_data:pd.DataFrame, columns=None):
        df_data = df_data.where(df_data.notnull(), None)
        if columns is None:
            columns = df_data.columns.values.tolist()
        sql_insert = """ INSERT INTO {table_name} ({col_list}) VALUES({data_holder}) """.format(
            table_name=table_name,
            col_list=",".join(columns),
            data_holder=",".join(["%s" for _ in columns])
        )

        # 去除转义字符
        data = [[pymysql.escape_string(str(ele)) for ele in innerlist] for innerlist in df_data.values.tolist()]

        start = 0
        chunk_size = 100

        try:
            self.configure.ping(reconnect=True)
            # 分批次插入
            while start < len(data):
                print(f"sql is {sql_insert}")
                print(f"data is {data[start:start + chunk_size]}")
                print("====================================")
                self.begin.executemany(sql_insert, data[start:start + chunk_size])
                start += chunk_size
            self.configure.commit()
            return ""
        except pymysql.err.ProgrammingError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.InternalError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.OperationalError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.InterfaceError as error:
            self.configure.rollback()
            self.configure.close()
            return error
        except pymysql.err.DataError as error:
            self.configure.rollback()
            self.configure.close()
            return error


    # 批量存入数据，有的更新，不存在的插入
    def bench_save(self, table_name, df_data:pd.DataFrame):
        """
        批量存入数据，如果是数据库已有的数据就进行更新，如果是数据库没有的数据就进行插入
        """
        df_data = df_data.where(df_data.notnull(), None)
        # 去除转义字符
        data = [[pymysql.escape_string(str(ele)) for ele in innerlist] for innerlist in df_data.values.tolist()]
        columns = df_data.columns.tolist()

        col_list = ",".join(columns)
        data_holder = ",".join(["%s" for _ in columns])
        update_fields = ",".join([f"{col} = VALUES({col}) " for col in columns])
    
        print(f"aaaaaa, : {update_fields}")

        sql_insert = """ INSERT INTO {table_name} ({col_list}) VALUES({data_holder}) ON DUPLICATE KEY UPDATE {update_fields} """.format(
            table_name = table_name,
            col_list = col_list,
            data_holder = data_holder,
            update_fields = update_fields
        )

        start = 0
        chunk_size = 1000

        try:
            self.configure.ping(reconnect=True)
            # 分批次插入
            while start < len(data):
                print(f"sql is {sql_insert}")
                print(f"data is {data[start:start + chunk_size]}")
                print("====================================")
                self.begin.executemany(sql_insert, data[start:start + chunk_size])
                start += chunk_size
            self.configure.commit()
            return ""
        except pymysql.err.ProgrammingError as error:
            self.configure.rollback()
            self.configure.close()
            raise Exception(error)
        except pymysql.err.InternalError as error:
            self.configure.rollback()
            self.configure.close()
            raise Exception(error)
        except pymysql.err.OperationalError as error:
            self.configure.rollback()
            self.configure.close()
            raise Exception(error)
        except pymysql.err.InterfaceError as error:
            self.configure.rollback()
            self.configure.close()
            raise Exception(error)
        except pymysql.err.DataError as error:
            self.configure.rollback()
            self.configure.close()
            raise Exception(error)

    # update语句
    # UPDATE 表名称 SET 列名称 = 新值 WHERE 列名称 = 某值
    def update(self, table, field: dict, where: dict):
        """
        :param table: 表名
        :param field: 需修改列 => {“a”: 1}
        :param where: 查询字段列 => {“b =”: 1}
        :return: 只有异常才有返回值
        """
        field_list = []
        for field_key, field_value in field.items():
            key = str(field_key)
            if type(field_value) == dict:
                field_value = json.dumps(field_value)
                field_value = field_value.replace("\\", "\\\\")
                field_value = field_value.replace("'", '\\\\"')
                field_string = "%s = '%s'" % (field_key, field_value)
                field_list.append(field_string)
            elif type(field_value) == int:
                field_string = '%s = %d' % (field_key, field_value)
                field_list.append(field_string)
            elif type(field_value) == float:
                field_string = '%s = %f' % (field_key, field_value)
                field_list.append(field_string)
            else:
                field_value = field_value
                field_value = field_value.replace("\\", "\\\\")
                field_value = field_value.replace("'", '\\\\"')
                field_string = "%s = '%s'" % (key, field_value)
                field_list.append(field_string)
        final_field = ','.join(field_list)

        where_str = ""
        for where_key, where_value in where.items():
            if where_value is None or where_value == "" or where_value == "None":
                continue
            elif type(where_value) == int:
                where_value = where_value
                where_str += " AND " + "%s" % where_key + " " + "%d" % where_value
            elif type(where_value) == float:
                where_value = where_value
                where_str += " AND " + "%s" % where_key + " " + "%f" % where_value
            else:
                where_value = where_value.replace("'", '"')
                where_str += " AND " + "%s" % where_key + " " + "'%s'" % where_value

        sql = 'UPDATE ' + table + ' SET ' + final_field + ' WHERE ' + ' 1 = 1 ' + where_str
        print(f"update sql is : {sql}")
        try:
            self.configure.ping(reconnect=True)
            self.begin.execute(sql)
            self.configure.commit()
        except pymysql.err.ProgrammingError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.InternalError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.OperationalError as error:
            self.configure.rollback()
            self.configure.close()
            raise MyConnectionException("未能连接数据库。")
        except pymysql.err.DataError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))

    # delete语句
    # DELETE FROM 表名称 WHERE 列名称 = 值
    def delete(self, table, where: dict):
        """
        :param table: 表名
        :param where: 查询字段列 => {“b =”: 1}
        :return: 只有异常才有返回值
        """
        where_str = ""
        for where_key, where_value in where.items():
            if where_value is None or where_value == "" or where_value == "None":
                continue
            elif type(where_value) == int:
                where_value = where_value
                where_str += " " + "%s" % where_key + " " + "%d" % where_value
            elif type(where_value) == float:
                where_value = where_value
                where_str += " " + "%s" % where_key + " " + "%f" % where_value
            else:
                where_value = where_value.replace("'", '"')
                where_str += " " + "%s" % where_key + " " + "'%s'" % where_value

        sql = 'DELETE FROM ' + table + ' WHERE ' + ' 1 = 1 AND' + where_str

        try:
            self.configure.ping(reconnect=True)
            self.begin.execute(sql)
            self.configure.commit()
        except pymysql.err.ProgrammingError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.InternalError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))
        except pymysql.err.OperationalError as error:
            self.configure.rollback()
            self.configure.close()
            raise MyConnectionException("未能连接数据库。")
        except pymysql.err.DataError as error:
            self.configure.rollback()
            self.configure.close()
            raise EfficiDaoException(str(error))

    def rollBack(self):
        self.configure.rollback()

    def commit(self):
        self.configure.commit()

if __name__ == '__main__':
    pass
    # 调用代码 update
    # db_result = db.update(
    #     table="platform_interface_list",
    #     field={
    #         "response": finally_resp,
    #         "status": status,
    #         "req_time": req_time,
    #         "resp_time": resp_time
    #     },
    #     where={"id =": inter_id}
    # )
    # 调用代码 insert
    # result = Db().insert(
    #     table="platform_business_list",
    #     field={
    #         "name": name,
    #         "description": description,
    #         "number": 0,
    #         "status": 2,
    #         "create_time": int(time.time()),
    #         "admin": admin
    #     }
    # )
    # 调用代码 select
    # article = db.select(
    #     field=["a.`id`", "a.`title`", "a.`description`"],
    #     table="article a INNER JOIN member AS m ON a.mid = m.id",
    #     where=__where,
    #     other="ORDER BY a.id DESC limit {}, {}".format((int(page_num) - 1) * int(page_size), page_size)
    # )