#!/usr/bin/env python3
# coding:utf-8
"""
@Author : Lucky Jason
@Email  : LuckyJasonone@gmail.com
@Description : null
"""
from flask import Flask
from utils import pool, API_PORT

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Jason Proxy Pool</h1>' + '\n' \
           + '<h3>/get: Get a proxy from proxy pool</h3>' + '\n' \
           + '<h3>/count: Get number of proxies</h3>'


@app.route('/get')
def get_proxy():
    return pool.get_one()[0].decode('utf8')


@app.route('/count')
def count():
    return str(pool.count())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT)
