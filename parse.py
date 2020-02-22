#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
import requests
import re
from lxml import etree

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
}


def parse_xc(url):  # 西刺代理
    return ['http://{}:{}'.format(ip, port) for ip, port in
            re.findall(r'<td>([\d+.]+)</td>\s*?<td>(\d+)</td>', requests.get(url, headers=headers, timeout=5).text)]


if __name__ == '__main__':
    print(parse_xc('https://www.xicidaili.com/nn/'))
