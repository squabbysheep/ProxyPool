import requests
import re

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
}


#
# url = 'https://www.kuaidaili.com/free/inha/1/'
# text = requests.get(url, headers=headers).text
# reg = r'<tr.*?>(\d+\.\d+\.\d+\.\d+)<.*?>(\d+)</td>.*?</tr>'
# print(text)
#

def parse_k(url):  # 快代理
    return ['http://{}:{}'.format(ip, port) for ip, port in re.findall(
        r'<tr.*?>(\d+\.\d+\.\d+\.\d+)<.*?>(\d+)</td>.*?</tr>', requests.get(url, headers=headers).text, re.S)]


print(parse_k('https://www.kuaidaili.com/free/inha/1/'))
