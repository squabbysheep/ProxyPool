#!/usr/bin/env python3
# coding:utf-8
"""
@Author : Lucky Jason
@Email  : LuckyJasonone@gmail.com
@Description : null
"""
import requests
import re

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
}


def parse_xc(url):  # 西刺代理
    return ['{}://{}:{}'.format(http.lower(), ip, port) for ip, port, http in
            re.findall(r'<td>([\d+.]+)</td>\s*?<td>(\d+)</td>.*?<td>([HhTtPpSs]+)</td>',
                       requests.get(url, headers=headers, timeout=5).text, re.S)]


def parse_66ip(url):  # 66免费代理
    return ['http://{}'.format(proxy) for proxy in
            re.findall(r'[\d.]+:\d+', requests.get(url, headers=headers, timeout=5).text)]


def parse_5u(url):  # 无忧代理
    reg = r'<ul.*?>(\d+\.\d+\.\d+\.\d+)<.*?>(\d+)</li>.*?<li>([高匿名透明]+)</li>.*?<li>([https]+)</li>'
    return ['{}://{}:{}'.format(http, ip, port) for ip, port, level, http in
            re.findall(reg, requests.get(url, headers=headers).text, re.S) if '匿' in level]


def parse_k(url):  # 快代理
    return ['{}://{}:{}'.format(http.lower(), ip, port) for ip, port, http in re.findall(
        r'<tr.*?>(\d+\.\d+\.\d+\.\d+)<.*?>(\d+)</td>.*?>([HhTtPpSs]+)<', requests.get(url, headers=headers).text, re.S)]


def parse_1(url):  # 私人公开代理接口
    return ['http://{}'.format(js.get("proxy")) for js in requests.get(url, headers=headers).json()]


def parse_free(url):
    return ['{}://{}:{}'.format(data['protocol'], data['ip'], data['port']) for data in
            (requests.get(url, headers=headers, timeout=5).json())['data']['data'] if data['anonymity'] == 2]


def parse_ni(url):  # 泥马代理
    text = requests.get(url, headers=headers).text
    _proxies = []
    for ip_port, http in re.findall(r'<td>(\d+\.\d+\.\d+\.\d+:\d+)</td>.*?<td>(H.*?)</td>', text, re.S):
        if 'HTTP,HTTPS' in http:
            _proxies.append('http://{}'.format(ip_port))
            _proxies.append('https://{}'.format(ip_port))
        elif 'HTTPS' in http:
            _proxies.append('https://{}'.format(ip_port))
        else:
            _proxies.append('http://{}'.format(ip_port))
    return _proxies


def parse_hai(url):  # IP海
    return ['{}://{}:{}'.format(http.lower(), ip, port) for ip, port, http in
            re.findall(r'<tr.*?(\d+\.\d+\.\d+\.\d+).*?(\d+).*?(H[HhTtPpSs]+)',
                       requests.get(url, headers=headers).text, re.S)]