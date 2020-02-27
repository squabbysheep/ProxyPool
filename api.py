#!/usr/bin/env python
# coding:utf-8
"""
@Author : Yuanmin Zhou
@Email  : 17859717522@163.com
@Description : null
"""
from flask import Flask
from scheduler import pool, API_PORT

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Jason Proxy Pool</h1>' + '\n' \
           + '<h3>/random: Get a proxy from proxy pool</h3>' + '\n' \
           + '<h3>/count: Get number of proxies</h3>' + '\n' \
           + '<h3>/all: Get all proxies from proxy pool</h3>'


@app.route('/random')
def get_proxy():
    proxies = pool.get_one()
    if proxies:
        return proxies[0].decode('utf8')
    return "THE POOL IS EMPTY."


@app.route('/count')
def count():
    return str(pool.count())


@app.route('/all')
def get_all():
    proxies = pool.get_all()
    if isinstance(proxies, set):
        proxies = [proxy.decode('utf8') for proxy in proxies]
    proxies = ['<p>{}<p>'.format(proxy) for proxy in proxies]
    return ''.join(proxies)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=API_PORT)
