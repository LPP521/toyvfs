class ToyVfsMixin:
    _disk_name = 'disk.toyvfs'
    _disk_size = 64 * 1024
    _file_limit = 64
    _header_size = 32
    _header_offset = 10
    _content_offset = 32 * 64
    _address_size = 2
