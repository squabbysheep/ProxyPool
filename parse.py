#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
import requests
import re

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
}


def parse_xc(url):  # 西刺代理
    return ['http://{}:{}'.format(ip, port) for ip, port in
            re.findall(r'<td>([\d+.]+)</td>\s*?<td>(\d+)</td>', requests.get(url, headers=headers, timeout=5).text)]


def parse_66ip(url):  # 66免费代理
    return ['http://{}'.format(proxy) for proxy in
            re.findall(r'[\d.]+:\d+', requests.get(url, headers=headers, timeout=5).text)]


def parse_5u(url):  # 无忧代理
    text = requests.get(url, headers=headers).text
    reg = r'<ul.*?>(\d+\.\d+\.\d+\.\d+)<.*?>(\d+)</li>.*?<li>([高匿名透明]+)</li>'
    return ['http://{}:{}'.format(ip, port) for ip, port, level in re.findall(reg, text, re.S) if level == '高匿']


def parse_k(url):  # 快代理
    return ['http://{}:{}'.format(ip, port) for ip, port in re.findall(
        r'<tr.*?>(\d+\.\d+\.\d+\.\d+)<.*?>(\d+)</td>.*?</tr>', requests.get(url, headers=headers).text, re.S)]


def parse_1(url):  # 私人公开代理接口
    return ['http://{}'.format(js.get("proxy")) for js in requests.get(url, headers=headers).json()]
