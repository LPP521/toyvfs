import time


def log(*args, **kwargs):
    format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    print(dt, *args, **kwargs)


def write_byte(path, address, byte):
    with open(path, 'rb+') as f:
        f.seek(address)
        f.write(byte)


def read_byte(path, address):
    with open(path, 'rb') as f:
        f.seek(address)
        byte = f.read(1)
        return byte


def write_bytes(path, address, bytes):
    with open(path, 'rb+') as f:
        f.seek(address)
        f.write(bytes)


def read_bytes(path, address, size):
    with open(path, 'rb') as f:
        f.seek(address)
        bytes = f.read(size)
        return bytes


def bytes_from_int(i, length=2, byteorder='little'):
    bytes = int(i).to_bytes(length=length, byteorder=byteorder)
    return bytes


def int_from_bytes(bytes, byteorder='little'):
    i = int.from_bytes(bytes, byteorder=byteorder)
    return i


def fill_bytes(bytes, length, fill_byte=b'\x00'):
    bs = bytes
    bytes_length = len(bytes)
    if length > bytes_length:
        bs = bytes + fill_byte * (length - bytes_length)
    return bs
