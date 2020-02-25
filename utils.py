#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
import asyncio
import json
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
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

file_handler_error = logging.FileHandler(os.path.join(log_dir, 'spider_error.log'), mode='a')  # 错误日志文件
file_handler_error.setLevel(logging.ERROR)
file_handler_error.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(file_handler_error)

file_handler_info = logging.FileHandler(os.path.join(log_dir, 'spider_info.log'), mode='w')  # 控制台日志文件
file_handler_info.setLevel(logging.INFO)
file_handler_info.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(file_handler_info)

console_handler = logging.StreamHandler()  # 控制台
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(console_handler)


class ProxyPoolAPI(object):
    def __init__(self, host, port, password, pool_name):
        self.conn = redis.Redis(host=host, port=port, password=password)
        self.pool_name = pool_name
        try:
            self.conn.exists(pool_name)  # 验证是否连接
        except Exception as redis_error:
            logging.error('REDIS ERROR - {}'.format(redis_error))
            logging.error('REDIS NO RUNNING, SYSTEM EXIT')
            sys.exit(0)

    def add(self, proxy):
        try:
            self.conn.sadd(self.pool_name, proxy)
        except Exception as unknown_error:
            logging.error('ADD PROXY ERROR - {}'.format(unknown_error))

    def rem(self, proxy):
        try:
            if self.conn.sismember(self.pool_name, proxy):
                self.conn.srem(self.pool_name, proxy)
        except Exception as unknown_error:
            logging.error('REMOVE PROXY ERROR - {}'.format(unknown_error))

    def count(self):
        try:
            return self.conn.scard(self.pool_name)
        except Exception as unknown_error:
            logging.error('GET COUNT OF PROXIES ERROR - {}'.format(unknown_error))

    def get_one(self):
        try:
            return self.conn.srandmember(self.pool_name, 1)
        except Exception as unknown_error:
            logging.error('GET ONE PROXY ERROR - {}'.format(unknown_error))

    def get_all(self):
        try:
            return self.conn.smembers(self.pool_name)
        except Exception as unknown_error:
            logging.error('GET ALL PROXIES ERROR - {}'.format(unknown_error))


pool = ProxyPoolAPI(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, pool_name=POOL_NAME)


async def test_single_proxy(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            if isinstance(proxy, bytes):
                proxy = proxy.decode('utf-8')
            if REJECT_NO_ANONYMITY_PROXY:
                async with session.get(TEST_URL_LEVER, proxy=proxy, timeout=7) as response:
                    if response.status == 200:
                        html = await response.read()
                        if proxy[7:].split(':')[0] == json.loads(html.decode('utf8')).get('origin'):
                            pool.add(proxy)
                            logging.info('ANONYMOUS PROXY: {}'.format(proxy))
                        else:
                            logging.info('TRANSPARENT PROXY: {}'.format(proxy))
                    else:
                        logging.info('INVALID PROXY: {}'.format(proxy))
            else:
                async with session.head(TEST_URL, proxy=proxy, timeout=7) as response:
                    if response.status == 200:
                        pool.add(proxy)
                        logging.info('VALID VALID: {}'.format(proxy))
                    else:
                        pool.rem(proxy)
                        logging.info('INVALID PROXY: {}'.format(proxy))
    except Exception as async_e:
        pool.rem(proxy)
        logging.info('INVALID PROXY: {}'.format(proxy))
        del async_e


def test_proxies(proxies):
    try:
        loop = asyncio.get_event_loop()
        tasks = [test_single_proxy(proxy) for proxy in proxies]
        loop.run_until_complete(asyncio.wait(tasks))
    except ValueError:
        logging.error('ASYNC ERROR')


def spider_cycle():
    now = int(time.time())
    logging.info('THE SPIDER COME TO WORK')
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
        logging.info('THE SPIDER SLEEPS FOR {} MINUTES'.format(SPIDER_CYCLE_INTERVAL))
        time.sleep(SPIDER_CYCLE_INTERVAL * 60)
        logging.info('THE SPIDER COMES TO CHECK AND WORK')


def test_pool_cycle():
    while True:
        proxies = pool.get_all()
        if proxies:
            test_proxies(proxies)
        time.sleep(PROXY_POOL_CYCLE_INTERVAL * 60)
        logging.info('THE POOL TEST SLEEPS FOR {} MINUTES'.format(PROXY_POOL_CYCLE_INTERVAL))


def get_ip():
    (status, output) = subprocess.getstatusoutput('ifconfig')
    if status == 0:
        return re.search(r'ppp0.*?inet.*?(\d+.\d+.\d+.\d+).*?netmask', output, re.S).group(1)


def replace_local_ip():
    (status, output) = subprocess.getstatusoutput('adsl-stop;adsl-start')
    if status == 0:
        ip = get_ip()
        logging.info('LOCAL IP UPDATED, NEW IP IS: {}'.format(ip))
        if TINY_PROXY:
            subprocess.getstatusoutput('systemctl restart tinyproxy.service')  # 解决服务挂掉问题
            proxy = 'http://{}:{}'.format(ip, TINY_PROXY_PORT)
            pool.add(proxy)
            logging.info('ANONYMOUS PROXY (LOCAL): {}'.format(proxy))
    else:
        logging.error('LOCAL IP UPDATE FAILED')


def replace_local_ip_cycle():
    time.sleep(REPLACE_LOCAL_IP_FIRST_WAIT * 60)
    while True:
        replace_local_ip()
        time.sleep(REPLACE_LOCAL_IP_CYCLE_INTERVAL * 60)
