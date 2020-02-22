#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
from multiprocessing import Process
from utils import spider_cycle, test_pool_cycle, replace_local_ip_cycle


def run():
    spider = Process(target=spider_cycle, name='spder_cycle')  # 不会停下来,没有返回值
    test = Process(target=test_pool_cycle, name='test_pool_cycle')
    local = Process(target=replace_local_ip_cycle, name='replace_local_ip_cycle')
    spider.start()
    test.start()
    local.start()


if __name__ == '__main__':
    run()
