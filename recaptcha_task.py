from yescaptcha.task import HCaptchaTaskProxyless, NoCaptchaTaskProxyless
from yescaptcha.task.base import BaseTaskProxyless


class TurnstileTaskProxylessM1(BaseTaskProxyless):
    type = "TurnstileTaskProxylessM1"


class TurnstileTaskProxyless(BaseTaskProxyless):
    type = "TurnstileTaskProxyless"


class TurnstileTaskS2(BaseTaskProxyless):
    type = "TurnstileTaskS2"

    def __init__(self, website_url, website_key, proxy, *args, **kwargs):
        self.proxy = proxy
        super().__init__(website_url, website_key, *args, **kwargs)

    def serialize(self):
        return {
            **super().serialize(),
            "proxy": self.proxy,
        }
