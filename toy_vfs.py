import os
from toy_vfs_mixin import ToyVfsMixin
from toy_vfs_file import ToyVfsFile
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


class ToyVfs(ToyVfsMixin):
    def __init__(self):
        self._init_disk()

    def _init_disk(self):
        if not os.path.exists(self._disk_name):
            self.format()

    def _valid_path(self, path):
        """ TODO: 判断路径是否合法 """
        return True

    def _parent_path_list(self, path):
        """ 
        返回父目录路径列表
        例如：
            '/' => []
            '/A' => ['/']
            '/A/B' => ['/', '/A']
            '/A/B/C' => ['/', '/A', '/A/B']
        """
        if path == '/':
            return []
        path_list = []
        for i, c in enumerate(path):
            if c == '/':
                path_list.append(path[0:i])
        path_list[0] = '/'
        return path_list
    
    @staticmethod
    def _type_mapper(type):
        mapper = {
            'dir': ToyVfsFile.TypeDir,
            'file': ToyVfsFile.TypeFile,
        }
        t = mapper[type]
        return t

    def format(self):
        # 初始化磁盘文件
        init_bytes = b'\x00' * self._disk_size
        write_bytes(self._disk_name, 0, init_bytes)
        # 写入磁盘文件头部
        disk_header = b'TOYVFS\x00\x00\x00\x00'
        write_bytes(self._disk_name, 0, disk_header)
        # 创建根目录
        self.make_dir('/')

    def dir_exist(self, path):
        """ 目录是否存在 """
        f = ToyVfsFile.file_from_path(path)
        return f is not None

    def make_dir(self, path, type='dir'):
        """ 创建目录, path 中不存在的目录都会被创建 """
        if not self._valid_path(path):
            return None
        if self.dir_exist(path):
            return None
        # 创建不存在的目录
        parent_path_list = self._parent_path_list(path)
        for parent_path in parent_path_list:
            if not self.dir_exist(parent_path):
                f = ToyVfsFile.new(parent_path, type=ToyVfsFile.TypeDir)
                if f is None:
                    return None
        #
        t = self._type_mapper(type)
        f = ToyVfsFile.new(path, t)
        return f

    def remove_dir(self, path):
        """ 删除路径, 如果参数是个目录则递归删除 """
        if not self._valid_path(path):
            return
        f = ToyVfsFile.file_from_path(path)
        if f is None:
            return
        f.remove()

    def list(self, path):
        """ 返回 path 下所有的子文件，以列表形式 """
        if not self._valid_path(path):
            return None
        f = ToyVfsFile.file_from_path(path)
        if f is None:
            return None
        l = f.children()
        return l

    def write(self, path, content):
        """ 把 content 写入 path 中，path 是一个文件 """
        if not self._valid_path(path):
            return
        f = ToyVfsFile.file_from_path(path)
        if not self.dir_exist(path):
            f = self.make_dir(path, type='file')
        if f is None:
            return
        f.write(content)

    def read(self, path):
        """ 返回 path 中给定的这个文件的内容 """
        if not self._valid_path(path):
            return None
        f = ToyVfsFile.file_from_path(path)
        if f is None:
            return None
        content = f.read()
        return content
