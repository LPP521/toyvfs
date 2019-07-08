# ToyVfs
一个 python 实现的虚拟文件系统，提供基本的文件增删改查功能

## 例子
```
from toy_vfs import ToyVfs


def main():
    vfs = ToyVfs()
    # 格式化磁盘文件
    vfs.format()
    #
    vfs.make_dir('/A')
    vfs.make_dir('/B')
    vfs.make_dir('/A/A')
    #
    print('path /:', vfs.list('/'))
    print('path /A:', vfs.list('/A'))
    print('path /B:', vfs.list('/B'))
    #
    vfs.write('/A/a', '吃饭')
    vfs.write('/A/b', '睡觉')
    vfs.write('/B/a', '写代码')
    #
    print('file /A/a:', vfs.read('/A/a'))
    print('file /A/b:', vfs.read('/A/b'))
    print('file /B/a:', vfs.read('/B/a'))
    #
    vfs.remove_dir('/A')
    print('path /:', vfs.list('/'))


if __name__ == '__main__':
    main()
```

## 设计
```
disk.toyvfs 为 64k 大小的虚拟磁盘文件，地址从低到高

0-5     TOYVFS（大端）
6-9     填 0，暂时不使用这 4 个字节
10      根目录的文件信息（文件信息的描述在下方，一共 32 字节）

文件信息，32 字节
文件名长度              1 个字节
文件名                 9 字节（大端）
文件类型                1 字节，0 表示文件，1 表示目录
文件长度（目录子文件数量） 2 字节（小端）
父目录地址              2 字节，0 表示没有父目录（只有根目录 / 是 0，小端）
同目录下一个文件地址    2 字节（只支持 64K 容量的硬盘），0 表示没有下一个文件了（小端）
文件内容开始的地址       2 字节，如果文件类型是目录则表示第一个子文件的文件信息地址（小端）
保留                   13 字节，填 0

文件内容，大小不定
文件信息地址            2 字节，反向指向文件信息（小端）

前 2k 为文件信息头部列表
```