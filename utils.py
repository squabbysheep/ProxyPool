#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
import asyncio
import subprocess
import sys
import aiohttp
import time
import redis
from setting import *
from parse import *

# POOL = redis.ConnectionPool(url=REDIS_URL, max_connections=100)
# conn = redis.Redis(connection_pool=POOL)
try:
    conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    conn.time()
except Exception as e:
    print('[ERROR][{}][REDIS NO RUNNING][{}]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), e))
    print('[LOG][{}][REDIS NO RUNNING,SYSTEM EXIT]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    sys.exit()


async def test_single_proxy(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            if isinstance(proxy, bytes):
                proxy = proxy.decode('utf-8')
            async with session.head(TEST_URL, proxy=proxy, timeout=10) as response:  # 请求头即可
                if response.status == 200:
                    conn.sadd(POOL_NAME, proxy)
                    print('[LOG][{}][{}]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), proxy))
                elif conn.sismember(POOL_NAME, proxy):
                    conn.srem(POOL_NAME, proxy)
    except Exception as e:
        del e


def test_proxies(proxies):
    try:
        loop = asyncio.get_event_loop()
        tasks = [test_single_proxy(proxy) for proxy in proxies]
        loop.run_until_complete(asyncio.wait(tasks))
    except ValueError:
        print('')
        print(
            '[ERROR][{}][ASYNC ERROR][PROXY={}]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), proxies))


def spider_cycle():
    now = int(time.time())
    for spider in SPIDER_CONFIGURE:
        spider.append(now)
        proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
        if proxies:
            test_proxies(proxies)
        else:
            print('[ERROR][{}][{}][NO PROXY]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), spider[0]))

    while True:
        now = int(time.time())
        for spider in SPIDER_CONFIGURE:
            if now - spider[3] >= spider[2] * 60:
                proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
                if proxies:
                    test_proxies(proxies)
                else:
                    print('[ERROR][{}][{}][NO PROXY]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                             spider[0]))
        time.sleep(SPIDER_CYCLE_INTERVAL)


def test_pool_cycle():
    while True:
        proxies = conn.smembers(POOL_NAME)
        if proxies:
            test_proxies(proxies)
        time.sleep(PROXY_POOL_CYCLE_INTERVAL * 60)


def replace_local_ip():
    (status, output) = subprocess.getstatusoutput('adsl-stop;adsl-start')
    if status == 0:
        print('[LOG][{}][LOCAL IP UPDATED]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    else:
        print('[ERROR][{}][LOCAL IP UPDATE FAILED]'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))


def replace_local_ip_cycle():
    time.sleep(REPLACE_LOCAL_IP_FIRST_WAIT)
    while True:
        replace_local_ip()
        time.sleep(REPLACE_LOCAL_IP_CYCLE_INTERVAL * 60)
