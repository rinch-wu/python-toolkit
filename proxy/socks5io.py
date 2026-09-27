# https://my.socks5.io/instruction/#/api_python?id=api%e6%8e%a5%e5%85%a5


import json
import threading
import time

import requests

"""
首先将外网IP加入白名单
"""


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
}


# TODO: 更新逻辑
# TODO: 删除print
# （http）业务逻辑
def execute_http(proxy_addr):
    targetUrl = "http://ip234.in/ip.json"

    proxies = {
        "http": "http://{}".format(proxy_addr),
        "https": "http://{}".format(proxy_addr),
    }
    res = ""

    while True:
        try:
            res = requests.get(targetUrl, proxies=proxies, timeout=5)
            break
        except Exception as e:
            print(e)
            break
    return


# (socks5) 业务逻辑
def execute_socks5(proxy_addr):
    targetUrl = "http://ip234.in/ip.json"

    proxies = {
        "http": "socks5h://{}".format(proxy_addr),
        "https": "socks5h://{}".format(proxy_addr),
    }
    res = ""

    while True:
        try:
            res = requests.get(targetUrl, proxies=proxies, timeout=5)
            # print(res.status_code)
            print(res.status_code, "***", res.text)
            break
        except Exception as e:
            print(e)
            break
    return


class ThreadFactory(threading.Thread):
    def __init__(self, proxy_addr, proxy_type):
        threading.Thread.__init__(self)
        self.proxy_addr = proxy_addr
        self.proxy_type = proxy_type

    def run(self):
        if self.proxy_type == "socks5":
            execute_socks5(self.proxy_addr)
        else:
            execute_http(self.proxy_addr)


def test_http():
    # 一次提5个 (text格式)
    get_proxy_url = (
        "http://api.socks5.io/user_get_ip_list?token=TOKEN&qty=5&country=&state=&city=&time=5&format=txt&filter=1"
    )

    while True:
        try:
            resp = requests.get(url=get_proxy_url, timeout=5)
            if resp.status_code != 200:
                print("提取IP失败")
                time.sleep(1)
                continue
            ips = resp.text.split("\r\n")
            threads = []
            for ip in ips:
                threads.append(ThreadFactory(ip, "http"))
            for t in threads:
                t.start()
                time.sleep(0.01)
            for t in threads:
                t.join()

            # break
            time.sleep(1)
        except Exception as e:
            print(e)


def test_socks5():
    # 一次提5个 (text格式)
    get_proxy_url = "http://api.socks5.io/user_get_ip_list?token=TOKEN&qty=5&country=&state=&city=&time=5&format=txt&protocol=http&filter=1"

    while True:
        try:
            resp = requests.get(url=get_proxy_url, timeout=5)
            if resp.status_code != 200:
                print("提取IP失败")
                time.sleep(1)
                continue
            ips = resp.text.split("\r\n")
            threads = []
            for ip in ips:
                threads.append(ThreadFactory(ip, "socks5"))
            for t in threads:
                t.start()
                time.sleep(0.01)
            for t in threads:
                t.join()

            # break
            time.sleep(1)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # 测试http
    # test_http()

    # 测试socks5
    test_socks5()
