import hashlib


def md5_encryption(msg, charset="utf-8"):
    """
    md5加密
    :param msg: 加密的字符串
    :param charset: 编码的字符集
    """
    md5 = hashlib.md5()
    md5.update(msg.encode(charset))
    encryption = md5.hexdigest()
    return encryption