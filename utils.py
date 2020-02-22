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
import logging
import os
from setting import *
from parse import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # 设置为最低

log_dir = os.path.join(os.getcwd(), 'Logs')
log_file = os.path.join(log_dir, 'spider_error.log')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

file_handler = logging.FileHandler(log_file, mode='a')  # 日志文件
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()  # 控制台
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(console_handler)

try:
    conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    conn.time()
except Exception as e:
    logging.error('REDIS NO RUNNING - {}'.format(e))
    logging.error('REDIS NO RUNNING,SYSTEM EXIT')
    sys.exit()


async def test_single_proxy(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            if isinstance(proxy, bytes):
                proxy = proxy.decode('utf-8')
            async with session.head(TEST_URL, proxy=proxy, timeout=10) as response:  # 请求头即可
                if response.status == 200:
                    conn.sadd(POOL_NAME, proxy)
                    logging.info(proxy)
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
        logging.error('ASYNC ERROR')


def spider_cycle():
    now = int(time.time())
    for spider in SPIDER_CONFIGURE:
        spider.append(now)
        proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
        if proxies:
            logging.info('CRAWL SUCCESS: URL={}'.format(spider[0]))
            test_proxies(proxies)
        else:
            logging.error('CRAWL ERROR: URL={}'.format(spider[0]))

    while True:
        now = int(time.time())
        for spider in SPIDER_CONFIGURE:
            if now - spider[3] >= spider[2] * 60:
                proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
                if proxies:
                    test_proxies(proxies)
                else:
                    logging.error('CRAWL ERROR: URL={}'.format(spider[0]))
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
        logging.info('LOCAL IP UPDATED')
    else:
        logging.error('LOCAL IP UPDATE FAILED')


def replace_local_ip_cycle():
    time.sleep(REPLACE_LOCAL_IP_FIRST_WAIT)
    while True:
        replace_local_ip()
        time.sleep(REPLACE_LOCAL_IP_CYCLE_INTERVAL * 60)
