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
    ['http://www.66ip.cn/mo.php', 'parse_66ip', 15],  # 混合
    ['http://www.66ip.cn/nmtq.php', 'parse_66ip', 15],  # 混合
    ['http://www.data5u.com/', 'parse_5u', 5],  # 高匿
    ['https://www.kuaidaili.com/free/inha/1/', 'parse_k', 30],  # 高匿
    ['http://118.24.52.95/get_all/', 'parse_1', 30],  # 高匿
]

# 爬虫循环检测间隔
SPIDER_CYCLE_INTERVAL = 1  # 默认1分钟检测一次

# 代理池循环检测间隔
PROXY_POOL_CYCLE_INTERVAL = 5  # 默认5分钟检测一次

# 测试网站
TEST_URL = 'http://www.baidu.com/'

# Redis
REDIS_HOST = '121.36.55.134'
REDIS_PORT = 8888
REDIS_PASSWORD = 123456
POOL_NAME = 'JASON_POOL'

# VPS
REPLACE_LOCAL_IP_FIRST_WAIT = 60  # second
REPLACE_LOCAL_IP_CYCLE_INTERVAL = 20  # minute
