#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
# 爬虫配置 [['url','parse','interval']] interval的单位是分钟
SPIDER_CONFIGURE = [
    ['https://www.xicidaili.com/nn/', 'parse_xc', 30],  # 高匿
    ['https://www.xicidaili.com/nn/2', 'parse_xc', 30],  # 高匿
    ['https://www.xicidaili.com/nt/', 'parse_xc', 30]  # 普通代理
]

# 爬虫循环检测间隔
SPIDER_CYCLE_INTERVAL = 1  # 默认1分钟检测一次

# 代理池循环检测间隔
PROXY_POOL_CYCLE_INTERVAL = 5  # 默认5分钟检测一次

# 测试网站
TEST_URL = 'http://www.baidu.com/'

# Redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = 123456
POOL_NAME = 'JASON_POOL'

# VPS
REPLACE_LOCAL_IP_FIRST_WAIT = 60  # second
REPLACE_LOCAL_IP_CYCLE_INTERVAL = 20  # minute
