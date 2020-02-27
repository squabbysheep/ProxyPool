#!/usr/bin/env python3
# coding:utf-8
"""
@Author : Lucky Jason
@Email  : LuckyJasonone@gmail.com
@Description : null
"""
# 爬虫配置 [['url','parse','interval']] interval的单位是分钟, 最低不得低于3分钟
SPIDER_CONFIGURE = [
    ['https://www.xicidaili.com/nn/', 'parse_xc', 10],  # 高匿
    ['https://www.xicidaili.com/nn/2', 'parse_xc', 10],  # 高匿
    ['http://www.data5u.com/', 'parse_5u', 5],  # 高匿
    ['https://www.kuaidaili.com/free/inha/1/', 'parse_k', 10],  # 高匿
    ['http://www.ip3366.net/free/?stype=1', 'parse_xc', 10],  # 高匿
    ['http://www.nimadaili.com/gaoni/1/', 'parse_ni', 5],  # 高匿
    ['http://www.nimadaili.com/gaoni/2/', 'parse_ni', 5],  # 高匿
    ['http://www.nimadaili.com/gaoni/3/', 'parse_ni', 5],  # 高匿
    ['http://www.nimadaili.com/gaoni/4/', 'parse_ni', 5],  # 高匿
    ['http://www.xiladaili.com/gaoni/1/', 'parse_ni', 5],  # 高匿
    ['http://www.xiladaili.com/gaoni/2/', 'parse_ni', 5],  # 高匿
    ['http://www.xiladaili.com/gaoni/3/', 'parse_ni', 5],  # 高匿
    ['http://www.xiladaili.com/gaoni/4/', 'parse_ni', 5],  # 高匿
    ['https://www.freeip.top/api/proxy_ips?page=1&country=中国', 'parse_free', 5],  # 混合
    ['https://www.freeip.top/api/proxy_ips?page=1&isp=电信', 'parse_free', 5],  # 混合
    ['https://www.freeip.top/api/proxy_ips?page=1&isp=阿里云', 'parse_free', 5],  # 混合
    ['https://www.freeip.top/api/proxy_ips?page=1&isp=移动', 'parse_free', 5],  # 混合
    ['https://www.freeip.top/api/proxy_ips?page=1&isp=联通', 'parse_free', 5],  # 混合
    ['http://www.iphai.com/', 'parse_hai', 5],  # 混合
    ['http://www.66ip.cn/mo.php', 'parse_66ip', 5],  # 混合
    ['http://www.66ip.cn/nmtq.php', 'parse_66ip', 5],  # 混合
    ['http://118.24.52.95/get_all/', 'parse_1', 5],  # 混合
]

# 爬虫循环检测间隔
SPIDER_CYCLE_INTERVAL = 1  # 默认1分钟检测一次

# 代理池循环检测间隔
PROXY_POOL_CYCLE_INTERVAL = 3  # 默认3分钟检测一次

# 测试网站(已经指定,此处指定无效)
# TEST_URL = 'http://httpbin.org/get'  # 'https://icanhazip.com/'

# 响应时间限制
HTTP_TIMEOUT = 4
HTTPS_TIMEOUT = 6

# Redis
REDIS_HOST = '121.36.55.134'
REDIS_PORT = 8888
REDIS_PASSWORD = 123456
POOL_NAME = 'JASON_PROXY_POOL'

# 代理池容量
POOL_CAPACITY_HTTP = (200, 400)
POOL_CAPACITY_HTTPS = (200, 400)

# VPS
REPLACE_LOCAL_IP_FIRST_WAIT = 2  # 默认等待1分钟
REPLACE_LOCAL_IP_CYCLE_INTERVAL = 15  # 默认15分钟替换一次

# VPS服务器上是否有tiny_proxy服务
TINY_PROXY = True
TINY_PROXY_PORT = 8888

# API
API_PORT = 80
