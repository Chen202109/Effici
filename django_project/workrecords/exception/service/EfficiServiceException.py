

class EfficiServiceException(Exception):
    def __init__(self, msg, status):
        self.msg = msg
        self.status = status

    def __str__(self):
        return self.msg