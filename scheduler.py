#!/usr/bin/env python3
# coding:utf-8
"""
@Author : Lucky Jason
@Email  : LuckyJasonone@gmail.com
@Description : null
"""
import asyncio
import json
import os
import subprocess
import time
from multiprocessing import Process
from multiprocessing import Queue
import aiohttp

from setting import *
from utils import *

log_dir = os.path.join(os.getcwd(), 'Logs')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# file log info
file_handler = logging.FileHandler(os.path.join(log_dir, 'info.log'), mode='a')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(file_handler)
# file log error
file_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'), mode='a')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(file_handler)
# console log
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(message)s]'))
logger.addHandler(console_handler)

pool = ProxyPoolAPI(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, pool_name=POOL_NAME)


def get_ip():
    (status, output) = subprocess.getstatusoutput('ifconfig')
    if status == 0:
        return re.search(r'ppp0.*?inet.*?(\d+.\d+.\d+.\d+).*?netmask', output, re.S).group(1)


local_ip = '125.81.15.117'  # get_ip()


async def test_single_proxy(proxy, origin_pool):
    # logging.error('FUNC=test_single_proxy')
    global local_ip
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head('http://www.baidu.com', proxy=proxy, timeout=HTTPS_TIMEOUT) as response:
                status_code = response.status
                if status_code == 200 and origin_pool:  # origin_pool 为 True
                    pool.add(proxy)
                    logging.debug('ANONYMOUS PROXY: {}'.format(proxy))
                elif status_code == 200:
                    async with session.get('http://httpbin.org/get', proxy=proxy,
                                           timeout=HTTPS_TIMEOUT * 2) as response1:
                        html = await response1.read()
                        if local_ip not in html:
                            pool.add(proxy)
                            logging.debug('ANONYMOUS PROXY: {}'.format(proxy))
                else:
                    pool.rem(proxy)
                    logging.debug('INVALID PROXY: {}'.format(proxy))
    except Exception as async_error:
        pool.rem(proxy)
        logging.debug('INVALID PROXY: {}'.format(proxy))
        # logging.error('async_error')
        del async_error


def test_http_proxies(proxies, origin_pool):
    try:
        loop = asyncio.get_event_loop()
        tasks = [test_single_proxy(proxy, origin_pool) for proxy in proxies]
        loop.run_until_complete(asyncio.wait(tasks))
    except ValueError:
        logging.error('ASYNC ERROR')


def put_https_proxies_to_queue(proxies_https, https_queue, origin_pool):
    for proxy in proxies_https:
        try:
            # https_queue = get_https_queue()
            https_queue.put('{}={}'.format(proxy, origin_pool), block=True, timeout=5)
        except Exception as full_error:
            logging.info('THE HTTPS QUEUE IS FULL: MES={}'.format(full_error))
            break


def test_https_proxies_process(https_queue):
    # https_queue = get_https_queue()
    global local_ip
    while True:
        proxy_origin_pool = https_queue.get(block=True)
        proxy, origin_pool = proxy_origin_pool.split('=')
        # logging.debug('DEBUG: proxy={},origin_pool={}'.format(proxy, origin_pool))
        proxy_dict = {
            'http': proxy,
            'https': proxy,
        }
        if origin_pool == 'True':
            try:
                response = requests.head('http://www.baidu.com', proxies=proxy_dict, timeout=HTTPS_TIMEOUT)
                if response.status_code == 200:
                    pool.add(proxy)
                    logging.debug('ANONYMOUS PROXY: {}'.format(proxy))
                else:
                    logging.debug('INVALID PROXY: {}'.format(proxy))
            except Exception as requests_error:
                # logging.debug('TIMEOUT: PROXY={}'.format(proxy))
                del requests_error
        else:
            try:
                response = requests.get('http://httpbin.org/get', proxies=proxy_dict, timeout=HTTPS_TIMEOUT * 2)
                html = response.text
                if local_ip in html:
                    pool.add(proxy)
                    logging.debug('ANONYMOUS PROXY: {}'.format(proxy))
                else:
                    logging.debug('TRANSPARENT PROXY: {}'.format(proxy))
            except Exception as requests_error:
                logging.debug('TIMEOUT: PROXY={}'.format(proxy))
                del requests_error


def test_proxies(proxies, https_queue, origin_pool):
    if isinstance(proxies, set):
        proxies = [proxy.decode('utf-8') for proxy in proxies]
    proxies_http = [proxy for proxy in proxies if 'https' not in proxy]
    proxies_https = [proxy for proxy in proxies if 'https' in proxy]
    if origin_pool:
        test_http_proxies(proxies_http, origin_pool)
        put_https_proxies_to_queue(proxies_https, https_queue, origin_pool)
    else:
        pool_proxies = pool.get_all()
        if isinstance(pool_proxies, set):
            pool_proxies = [proxy.decode('utf-8') for proxy in pool_proxies]
        pool_proxies_http = [proxy for proxy in pool_proxies if 'https' not in proxy]
        pool_proxies_https = [proxy for proxy in pool_proxies if 'https' in proxy]
        if len(pool_proxies_http) < POOL_CAPACITY_HTTP[1]:
            test_http_proxies(proxies_http, origin_pool)
        else:
            logging.info('THE PROXY POOL IS FULL, STOP ADD HTTP PROXIES ...')
        if len(pool_proxies_https) < POOL_CAPACITY_HTTPS[1]:
            put_https_proxies_to_queue(proxies_https, https_queue, origin_pool)
        else:
            logging.info('THE PROXY POOL IS FULL, STOP ADD HTTPS PROXIES ...')


def spider_cycle(https_queue):
    now = int(time.time())
    logging.info('THE SPIDER COME TO WORK')
    for spider in SPIDER_CONFIGURE:
        spider.append(now)
        proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
        if proxies:
            logging.info('CRAWL SUCCESS: URL={}'.format(spider[0]))
            test_proxies(proxies, https_queue, False)
        else:
            logging.error('CRAWL ERROR: URL={}'.format(spider[0]))
    while True:
        logging.info('THE SPIDER SLEEPS FOR {} MINUTES'.format(SPIDER_CYCLE_INTERVAL))
        time.sleep(SPIDER_CYCLE_INTERVAL * 60)
        logging.info('THE SPIDER COMES TO CHECK AND WORK')
        pool_proxies = pool.get_all()
        if isinstance(pool_proxies, set):
            pool_proxies = [proxy.decode('utf-8') for proxy in pool_proxies]
        pool_proxies_http = [proxy for proxy in pool_proxies if 'https' not in proxy]
        pool_proxies_https = [proxy for proxy in pool_proxies if 'https' in proxy]
        if len(pool_proxies_http) > POOL_CAPACITY_HTTP[0] and len(pool_proxies_https) > POOL_CAPACITY_HTTPS[0]:
            logging.info('THE PROXY POOL IS FULL, SPIDER SLEEPING ...')
            continue
        now = int(time.time())
        for spider in SPIDER_CONFIGURE:
            if now - spider[3] >= spider[2] * 60:
                spider[3] = now
                try:
                    proxies = eval('{0}("{1}")'.format(spider[1], spider[0]))
                    if proxies:
                        test_proxies(proxies, https_queue, False)
                    else:
                        logging.error('CRAWL ERROR: URL={}'.format(spider[0]))
                except Exception as req_error:
                    logging.error('CRAWL ERROR: IP WAS SEALED, URL={}, MES={}'.format(spider[0], req_error))


def test_pool_cycle(https_queue):
    logging.info('THE POOL TESTER COMES TO CHECK AND WORK')
    while True:
        proxies = pool.get_all()
        if proxies:
            test_proxies(proxies, https_queue, 'pool')
        time.sleep(PROXY_POOL_CYCLE_INTERVAL * 60)
        logging.info('THE POOL TESTER SLEEPS FOR {} MINUTES'.format(PROXY_POOL_CYCLE_INTERVAL))


def replace_local_ip():
    global local_ip
    (status, output) = subprocess.getstatusoutput('adsl-stop;adsl-start')
    if status == 0:
        ip = get_ip()
        local_ip = ip
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


def run():
    https_queue = Queue(300)
    spider = Process(target=spider_cycle, name='spider_cycle', args=(https_queue,))
    test = Process(target=test_pool_cycle, name='test_pool_cycle', args=(https_queue,))
    local = Process(target=replace_local_ip_cycle, name='replace_ip_cycle')
    https_process = Process(target=test_https_proxies_process, args=(https_queue,))

    spider.start()
    test.start()
    local.start()
    https_process.start()
