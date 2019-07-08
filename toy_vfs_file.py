import os
from toy_vfs_mixin import ToyVfsMixin
from utils import (
    log,
    write_byte,
    write_bytes,
    read_byte,
    read_bytes,
    bytes_from_int,
    int_from_bytes,
    fill_bytes,
)

class ToyVfsFile(ToyVfsMixin):
    TypeFile = 0
    TypeDir = 1

    def __init__(self, **kwargs):
        self.path = kwargs['path']
        self.name = kwargs['name']
        self.name_length = kwargs['name_length']
        self.type = kwargs['type']
        self.size = kwargs['size']
        self.address = kwargs['address']
        self.parent_address = kwargs['parent_address']
        self.next_address = kwargs['next_address']
        self.content_address = kwargs['content_address']

    @classmethod
    def _path_from_address(cls, address):
        bs = read_bytes(cls._disk_name, address, cls._header_size)
        name_length = bs[0]
        name = bs[1:10][0:name_length].decode('utf-8')
        name_list = [name]
        parent_address = int_from_bytes(bs[13:15])
        while parent_address != 0:
            bs = read_bytes(cls._disk_name, parent_address, cls._header_size)
            name_length = bs[0]
            name = bs[1:10][0:name_length].decode('utf-8')
            name_list.append(name)
            parent_address = int_from_bytes(bs[13:15])
        name_list = name_list[0:-1]
        name_list.reverse()
        path = '/{}'.format('/'.join(name_list))
        return path

    @classmethod
    def _file_from_address(cls, address):
        bs = read_bytes(cls._disk_name, address, cls._header_size)
        name_length = bs[0]
        if name_length == 0:
            return None
        name = bs[1:10][0:name_length].decode('utf-8')
        type = bs[10]
        size = int_from_bytes(bs[11:13])
        parent_address = int_from_bytes(bs[13:15])
        next_address = int_from_bytes(bs[15:17])
        content_address = int_from_bytes(bs[17:19])
        path = cls._path_from_address(address)
        f = cls(
            path=path,
            name_length=name_length,
            name=name,
            type=type,
            size=size,
            address=address,
            parent_address=parent_address,
            next_address=next_address,
            content_address=content_address,
        )
        return f

    @classmethod
    def _find_child_by_name(cls, parent, name):
        if parent.type != cls.TypeDir:
            return None
        child_address = parent.content_address
        if child_address == 0:
            return None
        child = cls._file_from_address(child_address)
        if child.name == name:
            return child
        while child.next_address != 0:
            child = cls._file_from_address(child.next_address)
            if child.name == name:
                return child
        return None

    @classmethod
    def _parent_address_from_path(cls, path):
        if path == '/':
            return 0
        parent_address = cls._header_offset
        dir_name_list = [p for p in path.split('/') if p != ''][0:-1]
        for i, dir_name in enumerate(dir_name_list):
            parent = cls._file_from_address(parent_address)
            if parent.content_address == 0:
                return parent_address
            child = cls._find_child_by_name(parent, dir_name)
            if child is None:
                return None
            parent_address = child.address
        return parent_address

    @classmethod
    def _params_from_path(cls, path, type):
        """ 文件创建参数 """
        if path == '/':
            name = '/'
        else:
            name = path.split('/')[-1]
        if name == '':
            return None
        parent_address = cls._parent_address_from_path(path)
        if parent_address is None:
            return None
        params = {
            'path': path,
            'name': name,
            'name_length': len(name.encode('utf-8')),
            'type': type,
            'size': 0,
            'address': 0,
            'parent_address': parent_address,
            'next_address': 0,
            'content_address': 0,
        }
        return params

    @classmethod
    def _new_address(cls):
        for i in range(0, cls._file_limit):
            address = cls._header_offset + i * cls._header_size
            header = read_bytes(cls._disk_name, address, cls._header_size)
            if header[0] == 0:
                return address
        return None

    def _update_link(self):
        """ 更新父目录和前后目录关系 """
        if self.parent_address == 0:
            return
        parent = self._file_from_address(self.parent_address)
        child_address = parent.content_address
        if child_address == 0:
            parent.content_address = self.address
            parent._save()
            return
        #
        child = self._file_from_address(child_address)
        if child.address == self.address:
            return
        while child.next_address != 0:
            child = self._file_from_address(child.next_address)
            if child.address == self.address:
                return
        child.next_address = self.address
        child._save()

    def _save(self):
        name = fill_bytes(self.name.encode('utf-8'), 9)
        name_length = bytes_from_int(self.name_length, length=1)
        type = bytes_from_int(self.type, length=1)
        size = bytes_from_int(self.size)
        parent_address = bytes_from_int(self.parent_address)
        next_address = bytes_from_int(self.next_address)
        content_address = bytes_from_int(self.content_address)
        pad = b'\00' * 13
        bs = name_length + name + type + size + parent_address + next_address + content_address + pad
        write_bytes(self._disk_name, self.address, bs)
        #
        self._update_link()

    def _prev(self):
        parent = self._file_from_address(self.parent_address)
        if parent.content_address == 0:
            return None
        prev = self._file_from_address(parent.content_address)
        while prev.next_address != self.address:
            prev = self._file_from_address(prev.next_address)
        return prev

    def _remove_header(self):
        bs = b'\x00' * self._header_size
        write_bytes(self._disk_name, self.address, bs)

    def _remove_children(self):
        if self.type == self.TypeDir:
            if self.content_address != 0:
                child = self._file_from_address(self.content_address)
                while child.next_address != 0:
                    address = child.next_address
                    child.remove()
                    child = self._file_from_address(address)
                child.remove()

    def _file_list(self):
        """ 返回 content 不为空的文件列表 """
        file_list = []
        for i in range(0, self._file_limit):
            address = self._header_offset + i * self._header_size
            f = self._file_from_address(address)
            if f is not None:
                if f.type == self.TypeFile and f.content_address != 0:
                    file_list.append(f)
        file_list = sorted(file_list, key=lambda f: f.content_address)
        return file_list

    def _new_content_address(self, content):
        length = len(content)
        file_list = self._file_list()
        address = self._content_offset
        for f in file_list:
            content_size = address + length + self._address_size
            if content_size > f.content_address:
                address = f.content_address + f.size + self._address_size
            else:
                return address
        content_size = address + length + self._address_size
        if content_size <= self._disk_size:
            return address
        return 0

    def write(self, content):
        if self.type != self.TypeFile:
            return
        content = content.encode('utf-8')
        content_address = self._new_content_address(content)
        if content_address == 0:
            return
        bs = content + bytes_from_int(self.address)
        write_bytes(self._disk_name, content_address, bs)
        self.content_address = content_address
        self.size = len(content)
        self._save()

    def read(self):
        if self.type != self.TypeFile:
            return None
        if self.content_address == 0:
            return None
        bs = read_bytes(self._disk_name, self.content_address, self.size)
        content = bs.decode('utf-8')
        return content

    def children(self):
        if self.type != self.TypeDir:
            return None
        child_address = self.content_address
        if child_address == 0:
            return []
        child = self._file_from_address(child_address)
        children = [child]
        while child.next_address != 0:
            child = self._file_from_address(child.next_address)
            children.append(child)
        return children

    def remove(self):
        if self.path == '/':
            return
        # 递归删除子目录
        self._remove_children()
        # 更新父目录第一个子文件信息
        parent = self._file_from_address(self.parent_address)
        if parent.content_address == self.address:
            parent.content_address = self.next_address
            parent._save()
            self._remove_header()
            return
        # 更新前一个文件的下一个文件地址
        prev = self._prev()
        prev.next_address = self.next_address
        prev._save()
        #
        self._remove_header()

    @classmethod
    def new(cls, path, type):
        params = cls._params_from_path(path, type)
        if params is None:
            return None
        #
        name = params.get('name', '')
        name_length = len(name.encode('utf-8'))
        if name_length == 0 or 9 < name_length:
            return None
        params['name'] = name
        params['name_length'] = name_length
        #
        address = cls._new_address()
        if address == 0:
            return None
        params['address'] = address
        f = cls(**params)
        f._save()
        return f
    
    @classmethod
    def file_from_path(cls, path):
        root_address = cls._header_offset
        root = cls._file_from_address(root_address)
        if root is None:
            return None
        if len(root.name) == 0:
            return None
        if path == '/':
            return root
        #
        parent_address = root_address
        dir_name_list = [p for p in path.split('/') if p != '']
        f = None
        for name in dir_name_list:
            parent = cls._file_from_address(parent_address)
            f = cls._find_child_by_name(parent, name)
            if f is None:
                return None
            parent_address = f.address
        return f

    def __repr__(self):
        if self.type == self.TypeDir:
            content = None
        else:
            content = self.read()
        s = '<\n    文件信息地址：{}\n    文件名长度：{}\n    文件名：{}\n    文件类型：{}\n    文件长度：{}\n    父目录地址：{}\n    同目录下一个文件地址：{}\n    文件内容地址：{}\n    文件内容：{}\n>'.format(
            self.address,
            self.name_length, 
            self.name,
            self.type,
            self.size,
            self.parent_address,
            self.next_address,
            self.content_address,
            content,
        )
        return s
