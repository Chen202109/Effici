import hashlib

def md5_encryption(msg, charset="utf-8"):
    md5 = hashlib.md5()
    md5.update(msg.encode(charset))
    encryption = md5.hexdigest()
    return encryption