import hashlib
def hash_(str):
    encoded = hashlib.md5(str.encode())
    identifier = int(encoded.hexdigest(), 16)
    return identifier