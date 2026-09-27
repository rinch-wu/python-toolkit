import random
from dataclasses import dataclass

import requests


@dataclass
class Socks5ioPoolConfig:
    username: str
    password: str


class Socks5ioPool:
    # https://my.socks5.io/pages/proxy/home

    def __init__(self, config: Socks5ioPoolConfig):
        self.config = config

    def url(self, account_id: str, dc: bool = True) -> str:
        """dc=True 动态住宅"""

        assert dc in (True, False, None)
        if dc == True:
            account_id = "dc_" + account_id
        elif dc == False:
            pass
        else:
            assert dc == None
            if random.random() < 0.5:
                account_id = "dc_" + account_id

        self._refresh(account_id)

        # curl -x socks5h://hongfei_1:mBCdBR@proxy.socks5.io:3003 myip.ipip.net

        url = f"http://{self.config.username}_{account_id}:{self.config.password}@proxy.socks5.io:3003"
        # print(f"{url=}")
        # proxies = {
        #     "http": url,
        #     "https": url,
        # }
        return url

    def _refresh(self, account_id: str):
        url = f"http://refresh.socks5.io/refresh?user={self.config.username}_{account_id}&country=us&state=&city="
        response = requests.get(url)
        assert response.status_code == 200, (response.status_code, response.text)
