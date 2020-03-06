#!/usr/bin/env python3
# coding:utf-8
"""
@Author : Lucky Jason
@Email  : LuckyJasonone@gmail.com
@Description : null
"""
from multiprocessing import Process
from utils import spider_cycle
from utils import test_pool_cycle
from utils import replace_local_ip_cycle


def run():
    spider = Process(target=spider_cycle, name='spider_cycle')  # 不会停下来,没有返回值
    test = Process(target=test_pool_cycle, name='test_pool_cycle')
    local = Process(target=replace_local_ip_cycle, name='replace_local_ip_cycle')
    spider.start()
    test.start()
    local.start()
    spider.join()
    test.join()
    local.join()


if __name__ == '__main__':
    run()
