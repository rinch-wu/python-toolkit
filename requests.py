import logging
import time

import retrying
from curl_cffi.requests import RequestsError as ConnectionError
from curl_cffi.requests import Response, get, post, put
from fake_useragent import UserAgent

from util_ import socks5io_pool

# from requests import ConnectionError, Response, get, post, put


class Requests:
    headers: dict[str]
    cookies: dict[str]
    proxies: dict[str, str]

    def __init__(self, address: str, use_proxies: bool = True, dc: bool = True):
        self.address = address
        self.use_proxies = use_proxies
        self.dc = dc

        self.set_proxies()

        ua = UserAgent(browsers=["chrome"], os=["windows"]).random
        # us_default = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
        self.headers = {
            "user-agent": ua,
            # "user-agent": us_default,
        }

        self.cookies = {}

    def add_header(self, k: str, v: str):
        self.headers[k] = v

    def add_cookie(self, k: str, v: str):
        self.cookies[k] = v

    def set_proxies(self):
        if self.use_proxies:
            address = self.address + str(int(time.time()))
            self.proxy = socks5io_pool.url(address, dc=self.dc)
            self.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
        else:
            self.proxy = None
            self.proxies = None

    def request_before(self, kwargs: dict[str]):
        kwargs["proxies"] = self.proxies
        kwargs["headers"] = kwargs.get("headers", {}) | self.headers
        kwargs["cookies"] = kwargs.get("cookies", {}) | self.cookies
        kwargs["verify"] = False
        return kwargs

    def request_after(self, response: Response):
        self.cookies.update(response.cookies)
        assert response.status_code < 300 or response.status_code == 304, (response.status_code, response.text)

    @retrying.retry(
        retry_on_exception=(ConnectionError,),
        wait_fixed=1000,
        stop_max_attempt_number=10,
    )
    def get(self, url, params=None, **kwargs):
        logging.info("get " + url)
        kwargs = self.request_before(kwargs)

        try:
            response = get(url=url, params=params, **kwargs)
        except ConnectionError as e:
            self.set_proxies()
            raise e

        self.request_after(response)
        data = response.json()
        return data

    @retrying.retry(
        retry_on_exception=(ConnectionError,),
        wait_fixed=1000,
        stop_max_attempt_number=10,
    )
    def post(self, url, data=None, json=None, **kwargs):
        logging.info("post " + url)
        kwargs = self.request_before(kwargs)

        try:
            response = post(url, data=data, json=json, **kwargs)
        except ConnectionError as e:
            self.set_proxies()
            raise e

        self.request_after(response)
        data = response.json()
        return data

    @retrying.retry(
        retry_on_exception=(ConnectionError,),
        wait_fixed=1000,
        stop_max_attempt_number=10,
    )
    def put(self, url, data=None, json=None, **kwargs):
        logging.info("put " + url)
        kwargs = self.request_before(kwargs)

        try:
            response = put(url=url, data=data, json=json, **kwargs)
        except ConnectionError as e:
            self.set_proxies()
            raise e

        self.request_after(response)
        data = response.json()
        return data

    @retrying.retry(
        retry_on_exception=(ConnectionError,),
        wait_fixed=1000,
        stop_max_attempt_number=10,
    )
    def get_origin(self, url, params=None, **kwargs):
        logging.info("get_origin " + url)
        kwargs = self.request_before(kwargs)

        try:
            response = get(url=url, params=params, **kwargs)
        except ConnectionError as e:
            self.set_proxies()
            raise e

        self.request_after(response)

        return response

    @retrying.retry(
        retry_on_exception=(ConnectionError,),
        wait_fixed=1000,
        stop_max_attempt_number=10,
    )
    def post_origin(self, url, data=None, json=None, **kwargs):
        logging.info("post_origin " + url)
        kwargs = self.request_before(kwargs)

        try:
            response = post(url=url, data=data, json=json, **kwargs)
        except ConnectionError as e:
            self.set_proxies()
            raise e

        self.request_after(response)

        return response

    def post_origin_noretry(self, url, data=None, json=None, **kwargs):
        logging.info("post_origin_noretry " + url)
        kwargs = self.request_before(kwargs)

        try:
            response = post(url=url, data=data, json=json, **kwargs)
        except ConnectionError as e:
            self.set_proxies()
            raise e

        self.request_after(response)

        return response
