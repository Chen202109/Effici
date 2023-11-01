import xlrd,uuid
# xlrd和xlwt是python的第三方库，xlrd模块实现对excel文件内容读取，xlwt模块实现对excel文件的写入

# ■■■■■■■ 该文件代码与 excel_workrecord.py 是一样的,改动一点地方。只是name_field不同，为将来方便调整而独立
# ■■■■■■■ 在privately文件夹下的mymain.py 中执行将license的申请记录导入到数据库

# 获取第一个表单的全部数据
# 根据不同的标题行，拼接出 insert into 指定列名，这个与 被插入的值要对应
# 因此拼接好的字段英文名，数据列表
def license_inster_sql(filePath):
    # excel的字段标题和 表的字段 对照关系
    name_field = {
        '环境':'environment','省份':'region','单位名称':'agenname','授权日期':'authorizeddate',
        '数据库类型':'databasetype','系统类型':'systemtype','签名服务器厂商':'signatureServerType'   # 安装时间不能加入，会报错，以后解决   ,'安装时间':'installtime'
    }

    book = xlrd.open_workbook(filePath)  # 加载excel
    sheet = book.sheet_by_index(0)  # 获取第一个sheet
    maxrow = sheet.nrows # 最大行数
    maxcol = sheet.ncols # 最大列数
    sql_key_str = 'fid,' # 保存拼接成的sql字段, ，先加固定的主键FID
    sql_key_col = [] # 保存sql字段所在的数据是第几列

    sql_value_str ="'"+''.join(str(uuid.uuid4()).split('-'))+"'," # 每一行的value数值内容，第一个数值为上面sql_key_str对应的FID

    sql_value_list = [] # 把所有行数据都保存进去

    for i in range(maxrow): #行循环
        if i == 0: # 0表示第一行，标题字段行
            for j in range(maxcol): # 1. 获取inster into 的字段名
                if sheet.cell_value(i,j) in name_field.keys(): # 当单元格的数据在字典中，说明是字段行（即第0行），通过字段顺序获得字典里面字段名，拼接成sql
                    sql_key_col.append(j) #记录j的数值，即记住是取了那些列的数据
                    sql_key_str = sql_key_str + str(name_field[f'{str(sheet.cell_value(i,j))}'])+',' # 拼接列上名字对应的字段, 最后用时要[:-1]，把最后的逗号去掉
                    print(f"{type(sheet.cell_value(i,j))},{sheet.cell_value(i,j)} 字段 {name_field[f'{str(sheet.cell_value(i,j))}']}")

        if i>0: #vlaue数据从第二行开始，# 2. 获取inster into 的字段名
            for n in range(len(sql_key_col)):
                # 也可以通过判断单元格类型是否为日期时间类型   # if worksheet.cell_type(rowx=0, colx=0) == xlrd.XL_CELL_DATE:

                if '时间' in sheet.cell_value(0,sql_key_col[n]): # 如果是 某某日期，那么需要用xldate_as_datetime将float转成日期
                    xldate_str = xlrd.xldate.xldate_as_datetime(sheet.cell_value(i, sql_key_col[n]), 0).strftime("%Y-%m-%d %H:%M:%S")
                    sql_value_str = sql_value_str + "'" + xldate_str + "'" + ","

                elif '日期' in sheet.cell_value(0,sql_key_col[n]):
                    xldate_str = xlrd.xldate.xldate_as_datetime(sheet.cell_value(i, sql_key_col[n]), 0).strftime("%Y-%m-%d")
                    sql_value_str = sql_value_str + "'" + xldate_str + "'" + ","

                    #print(sql_key_col[n]-1,sheet.cell_value(0, sql_key_col[n]-1),xlrd.xldate.xldate_as_datetime(sheet.cell_value(i, sql_key_col[n]-1), 0).strftime("%Y-%m-%d")) #检查取出的日期
                    #print(f'日期在 第{i + 1}行，第{sql_key_col[n] + 1}列{sheet.cell_value(0, sql_key_col[n])}')
                else:
                    #print(f'当前第{i+1}行，第{sql_key_col[n]+1}列{sheet.cell_value(0,sql_key_col[n])}')
                    sql_value_str = sql_value_str +"'"+str(sheet.cell_value(i,sql_key_col[n])).replace("'","").replace('"','')+"'"+','

            sql_value_list.append(sql_value_str[:-1]) # 为value数据列表，填充数据，-1是去掉最后的逗号
            sql_value_str ="'"+''.join(str(uuid.uuid4()).split('-'))+"',"  # 组装完一行数据，就清空一下

    # 验证取的信息对不对
    # print(f"被对照到的key字段：{sql_key_str}")
    # print(f'所有数据加载信息：')
    for s in range(len(sql_value_list)):
        print(f'{sql_value_list[s]}')

    # 返回拼接好的字段英文名，数据列表, 这里要注意，列名字段最后一个有逗号，要去掉
    return sql_key_str[:-1],sql_value_list

if __name__ == '__main__':
    # 这个是用于将 数据先复制下来，保存到excel后，导入过去。此py文件只是读取出来数据给privately--->mymain.py用
    file_path = f'C:\\Users\\Administrator\\Downloads\\license数据导入文件.xlsx'
    license_inster_sql(file_path)