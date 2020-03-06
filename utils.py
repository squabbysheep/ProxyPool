#!/usr/bin/env python3
# coding:utf-8
"""
@Author : Lucky Jason
@Email  : LuckyJasonone@gmail.com
@Description : null
"""
import os
import sys
import time
import json
import redis
import logging
import asyncio
import aiohttp
import subprocess
from multiprocessing import Process
from setting import *
from parse import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # 设置为最低

log_dir = os.path.join(os.getcwd(), 'Logs')
log_file = os.path.join(log_dir, '{}_proxy_pool.log'.format(time.strftime('%Y%m%d')))
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

file_handler = logging.FileHandler(log_file, mode='a')  # 日志文件
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(level{})s][%(asc{})s][%(message)s]'.format('name', 'time')))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()  # 控制台
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('[%(level{})s][%(asc{})s][%(message)s]'.format('name', 'time')))
logger.addHandler(console_handler)


class ProxyPoolAPI(object):
    def __init__(self, host, port, password, pool_name):
        self.conn = redis.Redis(host=host, port=port, password=password)
        self.pool_name = pool_name
        try:
            self.conn.exists(pool_name)  # 验证是否连接
        except Exception as redis_error:
            logging.error('Redis error - {}'.format(redis_error))
            logging.error('Redis no running, system exit')
            sys.exit(0)

    def add(self, proxy):
        try:
            self.conn.sadd(self.pool_name, proxy)
        except Exception as unknown_error:
            logging.error('Add proxy error - {}'.format(unknown_error))

    def rem(self, proxy):
        try:
            if self.conn.sismember(self.pool_name, proxy):
                self.conn.srem(self.pool_name, proxy)
        except Exception as unknown_error:
            logging.error('Remove proxy error - {}'.format(unknown_error))

    def count(self):
        try:
            return self.conn.scard(self.pool_name)
        except Exception as unknown_error:
            logging.error('Get count of proxies error - {}'.format(unknown_error))

    def get_one(self):
        try:
            return self.conn.srandmember(self.pool_name, 1)
        except Exception as unknown_error:
            logging.error('Get one proxy error - {}'.format(unknown_error))

    def get_all(self):
        try:
            return self.conn.smembers(self.pool_name)
        except Exception as unknown_error:
            logging.error('Get all proxies error - {}'.format(unknown_error))


pool = ProxyPoolAPI(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, pool_name=POOL_NAME)


async def test_single_proxy(proxy):
    global local_ip
    global pool
    try:
        async with aiohttp.ClientSession() as session:
            if isinstance(proxy, bytes):
                proxy = proxy.decode('utf-8')
                async with session.head(TEST_URL, proxy=proxy, timeout=3) as response:  # 请求头即可
                    if response.status == 200:
                        logging.info('Still valid: {}'.format(proxy))
                        pool.add(proxy)
                    else:
                        logging.info('Invalid proxy: {}'.format(proxy))
                        pool.rem(proxy)
            else:
                async with session.get(TEST_URL_LEVER, proxy=proxy, timeout=5) as response:  # 请求头即可
                    if response.status == 200:
                        html = await response.read()
                        # if proxy[7:].split(':')[0] == json.loads(html.decode('utf8')).get('origin'):
                        if local_ip != json.loads(html.decode('utf8')).get('origin'):
                            logging.info('Anonymous proxy: {}'.format(proxy))
                            pool.add(proxy)
                        else:
                            logging.info('Transparent proxy: {}'.format(proxy))
                    else:
                        logging.info('Invalid proxy: {}'.format(proxy))
    except Exception as async_e:
        logging.info('Invalid proxy: {}'.format(proxy))
        pool.rem(proxy)
        del async_e


def test_proxies(proxies):
    try:
        loop = asyncio.get_event_loop()
        tasks = [test_single_proxy(proxy) for proxy in proxies]
        loop.run_until_complete(asyncio.wait(tasks))
    except ValueError:
        logging.error('Async error')
    return None


def spider_cycle():
    spider_cycle_count = 0
    while True:
        spider_cycle_count += 1
        logging.warning('spider_cycle_count={}'.format(spider_cycle_count))
        try:
            logging.info('The spider come to work')
            for spider in SPIDER_CONFIGURE:
                proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
                proxies = [proxy.replace('s', '') for proxy in proxies]
                pool_proxies = pool.get_all()
                proxies = list(set(proxies) - set(pool_proxies))
                if proxies:
                    logging.info('Crawl success: URL={}'.format(spider[0]))
                    process = Process(target=test_proxies, args=(proxies,))
                    process.start()
                    for i in range(int(len(proxies) * 0.8)):
                        if not process.is_alive():
                            break
                        time.sleep(5)
                    if process.is_alive():
                        process.terminate()
                        logging.error('Crawl timeout: URL={}'.format(spider[0]))
                else:
                    logging.error('Crawl error: URL={}'.format(spider[0]))
        except Exception as error:
            del error
            logging.error('Spider cycle appear error.')

        logging.info('The spider sleeps for {} minutes'.format(SPIDER_CYCLE_INTERVAL))
        time.sleep(SPIDER_CYCLE_INTERVAL * 60)


def test_pool_cycle():
    while True:
        proxies = pool.get_all()
        if proxies:
            test_proxies(proxies)
        time.sleep(PROXY_POOL_CYCLE_INTERVAL * 60)
        logging.info('The pool test sleeps for {} minutes'.format(PROXY_POOL_CYCLE_INTERVAL))


def get_ip():
    (status, output) = subprocess.getstatusoutput('ifconfig')
    if status == 0:
        search = re.search(r'ppp0.*?net.*?(\d+\.\d+\.\d+\.\d+).*?netmask', output, re.S)
        if search:
            return search.group(1)
        else:
            return None


local_ip = get_ip()


def replace_local_ip():
    (status, output) = subprocess.getstatusoutput('{}l-stop;{}l-start'.format('ads', 'ads'))
    if status == 0:
        global local_ip
        local_ip = get_ip()
        if not local_ip:
            logging.critical('No ip, system exit.')
            sys.exit(0)
        ip = local_ip
        logging.info('Local ip updated, new ip is: {}'.format(ip))
        if TINY_PROXY:
            subprocess.getstatusoutput('{}ctl restart {}proxy.service'.format('system', 'tiny'))  # 解决服务挂掉问题
            proxy = 'http://{}:{}'.format(ip, TINY_PROXY_PORT)
            pool.add(proxy)
            logging.info('Anonymous proxy (local): {}'.format(proxy))
    else:
        logging.error('Local ip update failed.')


def replace_local_ip_cycle():
    time.sleep(REPLACE_LOCAL_IP_FIRST_WAIT * 60)
    while True:
        replace_local_ip()
        time.sleep(REPLACE_LOCAL_IP_CYCLE_INTERVAL * 60)

# if __name__ == '__main__':
#     local_ip = get_ip()
#     spider = Process(target=spider_cycle, name='spider_cycle')  # 不会停下来,没有返回值
#     test = Process(target=test_pool_cycle, name='test_pool_cycle')
#     local = Process(target=replace_local_ip_cycle, name='replace_local_ip_cycle')
#     spider.start()
#     test.start()
#     local.start()
