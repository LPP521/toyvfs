from toy_vfs import ToyVfs
from utils import log


def test():
    vfs = ToyVfs()
    # 格式化磁盘文件
    vfs.format()
    #
    vfs.make_dir('/A')
    vfs.make_dir('/B')
    vfs.make_dir('/A/A')
    #
    vfs.write('/A/a', '吃饭')
    vfs.write('/A/b', '睡觉')
    vfs.write('/B/a', '写代码')
    #
    assert vfs.read('/A/a') == '吃饭'
    assert vfs.read('/A/b') == '睡觉'
    assert vfs.read('/B/a') == '写代码'
    #
    log('path /:', vfs.list('/'))
    # log('path /A:', vfs.list('/A'))
    # log('path /B:', vfs.list('/B'))
    #
    vfs.remove_dir('/A/a')
    # log('path /A:', vfs.list('/A'))
    # vfs.remove_dir('/A/b')
    # log('path /A:', vfs.list('/A'))
    # vfs.remove_dir('/')
    # log('path /:', vfs.list('/'))


if __name__ == '__main__':
    test()
