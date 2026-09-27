# https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/4685944/reCaptcha

import os
import requests
import retrying

CLIENT_KEY = os.getenv("YESCAPTCHA_CLIENT_KEY", "")
TYPE = "NoCaptchaTaskProxyless"  # 验证码类型，reCaptchaV2 是 NoCaptchaTaskProxyless
# REFERER = 'https://www.google.com/recaptcha/api2/demo'
REFERER = "https://www.google.com/recaptcha/api2/anchor"
BASE_URL = "http://api.yescaptcha.com"


class YesCaptcha:
    @staticmethod
    @retrying.retry(stop_max_attempt_number=10)
    def create_task(site_key: str) -> str:
        url = f"{BASE_URL}/createTask"
        data = {"clientKey": CLIENT_KEY, "task": {"websiteURL": REFERER, "websiteKey": site_key, "type": TYPE}}
        try:
            response = requests.post(url, json=data, verify=False)
            assert response.status_code == 200
            return response.json()["taskId"]
        except requests.RequestException as e:
            raise ("create task failed", e)
        except Exception as e:
            raise (e)

    @staticmethod
    @retrying.retry(wait_fixed=1000, stop_max_attempt_number=1000, stop_max_delay=2 * 60 * 1000)
    def polling_task(task_id: str) -> str:
        url = f"{BASE_URL}/getTaskResult"
        params = {"clientKey": CLIENT_KEY, "taskId": task_id}
        try:
            response = requests.post(url, json=params, verify=False)
        except requests.RequestException as e:
            raise Exception("polling task failed", e)

        resp_data = response.json()
        YesCaptcha.__sign_error(response)
        status = resp_data["status"]
        if status == "ready":
            return resp_data["solution"]["gRecaptchaResponse"]
        elif status == "processing":
            raise Exception(f"polling_task time out, task_id={task_id}", resp_data)

    @staticmethod
    def __sign_error(response):
        if response.status_code != 200:
            raise Exception(f"status_code={response.status_code}, !=200")
        resp_data = response.json()
        if resp_data.get("errorId", 0) == 1:
            raise Exception(f"There is errerId, ", resp_data)
