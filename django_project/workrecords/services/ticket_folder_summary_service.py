from mydata import mysql_base

def get_customer_service_robot_summary(begin_date, end_date, db=None):
    """
    查询筛选范围时间内的票夹客服机器人的汇总数据。
    :param begin_date 起始日期
    :param end_date 终止日期
    :param db 数据库连接
    """
    db = get_db(db)
    condition_dict = {
        "date>=": begin_date,
        "date<=": end_date,
    }
    data = db.select(["date","sessionAmount","msgAmount","precision1","recall"], "ticket_folder_customer", condition_dict, " ORDER BY date ")
    return data

def get_db(db):
    if db is None:
        db = mysql_base.Db()
    return db