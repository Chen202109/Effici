from workrecords.exception.dao.EfficiDaoException import EfficiDaoException


class MyUnavailableException(EfficiDaoException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg