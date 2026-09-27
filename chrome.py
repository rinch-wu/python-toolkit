import json
import logging
import platform
import time

import cv2
import numpy as np
from fake_useragent import UserAgent

# from selenium.webdriver import Chrome, ChromeOptions
from seleniumwire.webdriver import Chrome, ChromeOptions

from .proxy._test_proxy import Proxy
from .selenium_ import *

import requests

# from webdriver_manager.chrome import ChromeDriverManager
# executable_path = ChromeDriverManager().install()


class MyChrome(Chrome):
    url_bot_test = "https://bot.sannysoft.com"
    stealthjs = requests.get("https://raw.githubusercontent.com/requireCool/stealth.min.js/main/stealth.min.js").text
    def __init__(self, url, proxy: str = None, path_crx_list: list[str] = []):
        options = ChromeOptions()

        # 去除ssl警告
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        # options.add_argument('--allow-insecure-localhost')

        # 去除自动控制提示
        options.add_argument("--disable-blink-features=AutomationControlled")

        # linux运行参数
        if platform.system() == "Linux":
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")

        # 获取日志（缓存）
        options.add_argument("--log-level=3")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        # 禁止日志（控制台、文件）
        options.add_argument("--disable-logging")
        options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])

        # options.add_argument("lang=zh-CN,zh,zh-TW,en-US,en")
        options.add_argument("lang=zh-CN,zh")

        # UA
        user_agent = UserAgent(browsers=["chrome"], os=["windows"]).random
        options.add_argument("--user-agent=" + str(user_agent))

        # 优化
        prefs = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",  # 禁止webrtc
            "webrtc.multiple_routes_enabled": False,  # 禁止webrtc
            "webrtc.nonproxied_udp_enabled": False,  # 禁止webrtc
            "profile.default_content_setting_values.images": 2,  # 禁止加载图片，加了这一句无法显示reCaptcha
            "permissions.default.stylesheet": 2,
        }
        options.add_experimental_option("prefs", prefs)

        for path_crx in path_crx_list:
            options.add_extension(path_crx)

        # 代理
        seleniumwire_options = proxy and {
            "proxy": {
                "http": proxy,
                "https": proxy,
            }
        }

        # super().__init__(executable_path, seleniumwire_options=seleniumwire_options, options=options)
        super().__init__(seleniumwire_options=seleniumwire_options, options=options)

        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": self.stealthjs})

        self.implicitly_wait(10)
        self.get(url)

    def get_response_body(self, url_req) -> str:
        assert (
            "performance" in self.log_types,
            "需要performance日志，请在添加webdriver启动参数：options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})",
        )
        perfs = self.get_log("performance")
        for row in perfs:
            message1 = row["message"]
            if not message1.startswith("{"):
                continue

            message1_json = json.loads(message1)
            message2_json = message1_json["message"]
            if message2_json["method"] != "Network.responseReceived":
                continue
            if message2_json["params"]["response"]["url"] != url_req:
                continue

            requestId = message2_json["params"]["requestId"]

            response_body = self.execute_cdp_cmd("Network.getResponseBody", {"requestId": requestId})
            return response_body["body"]

        raise Exception("请求不存在，", url_req)

    def waitTwoHandles(self, timeout=20):
        return WebDriverWait(self, timeout, 0.5).until(lambda driver: len(self.window_handles) == 2)

    def wait_element_clickable(self, xpath: str, timeout=20):
        return WebDriverWait(self, timeout, 0.5).until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def wait_element_located(self, xpath: str, timeout=10):
        return WebDriverWait(self, timeout, 0.5).until(EC.presence_of_element_located((By.XPATH, xpath)))

    def wait_element_miss(self, xpath: str, timeout=2):
        return WebDriverWait(self, timeout, 0.5).until_not(EC.presence_of_element_located((By.XPATH, xpath)))

    def find_element_nonable(self, xpath: str):
        element_list = self.find_elements(By.XPATH, xpath)
        result = element_list[0] if element_list else None
        return result

    def onlyOneWindow(self, waitTwoWindows=False):
        if waitTwoWindows:
            while len(self.window_handles) == 1:
                time.sleep(1)
        while len(self.window_handles) > 1:
            self.switch_to.window(self.window_handles[1])
            self.close()
            self.switch_to.window(self.window_handles[0])

    def clickByJs(self, xpath: str):
        self.execute_script(f"""document.evaluate("{xpath}",document).iterateNext().click()""")

    def leaveNewWindows(self):
        self.execute_script('window.open("")')
        self.switch_to.window(self.window_handles[0])
        self.close()
        self.switch_to.window(self.window_handles[0])

    def handleLogin(loginedSet: set, url: str) -> bool:
        if url in loginedSet:
            return True
        else:
            loginedSet.add(url)
            return False

    def find_by_data_testid(self, data_testid: str):
        return self.find_element(By.XPATH, f"//*[@data-testid='{data_testid}']")

    def get_scroll_page(self, file_name):
        logging.debug(f"{file_name=}")
        driver = self
        image_bytes_list = []
        window_height = driver.get_window_size()["height"]  # 窗口高度

        page_height = driver.execute_script("return document.documentElement.scrollHeight")  # 页面高度
        image_bytes_list.append(driver.get_screenshot_as_png())

        if page_height > window_height:
            n = page_height // window_height  # 需要滚动的次数
            for i in range(n):
                driver.execute_script(f"document.documentElement.scrollTop={window_height * (i + 1)};")
                time.sleep(0.5)
                image_bytes_list.append(driver.get_screenshot_as_png())

        image_list = [
            cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR) for image_bytes in image_bytes_list
        ]
        image = np.concatenate(image_list, axis=0)
        cv2.imwrite(file_name, image)

        return image
