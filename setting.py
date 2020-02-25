#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
# 爬虫配置 [['url','parse','interval']] interval的单位是分钟
SPIDER_CONFIGURE = [
    ['https://www.xicidaili.com/nn/', 'parse_xc', 10],  # 高匿
    ['https://www.xicidaili.com/nn/2', 'parse_xc', 10],  # 高匿
    ['http://www.66ip.cn/mo.php', 'parse_66ip', 3],  # 混合
    ['http://www.66ip.cn/nmtq.php', 'parse_66ip', 3],  # 混合
    ['http://www.data5u.com/', 'parse_5u', 3],  # 高匿
    ['https://www.kuaidaili.com/free/inha/1/', 'parse_k', 10],  # 高匿
    ['http://118.24.52.95/get_all/', 'parse_1', 5],  # 混合
]

# 是否剔除非高匿代理
REJECT_NO_ANONYMITY_PROXY = False  # 默认为True,剔除非高匿代理

# 爬虫循环检测间隔
SPIDER_CYCLE_INTERVAL = 1  # 默认1分钟检测一次

# 代理池循环检测间隔
PROXY_POOL_CYCLE_INTERVAL = 3  # 默认3分钟检测一次

# 测试网站
TEST_URL = 'http://www.baidu.com/'
TEST_URL_LEVER = 'http://httpbin.org/get'

# Redis
REDIS_HOST = '121.36.55.134'
REDIS_PORT = 8888
REDIS_PASSWORD = 123456
POOL_NAME = 'JASON_POOL'

# VPS
REPLACE_LOCAL_IP_FIRST_WAIT = 2  # 默认等待1分钟
REPLACE_LOCAL_IP_CYCLE_INTERVAL = 15  # 默认20分钟替换一次

# VPS服务器上是否有tiny_proxy服务
TINY_PROXY = True
TINY_PROXY_PORT = 8888

# API
API_PORT = 80
