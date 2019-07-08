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
