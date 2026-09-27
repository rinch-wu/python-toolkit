from loguru import logger
from yescaptcha.client import Client
from yescaptcha.task.base import BaseTask

logger.remove()


class Recaptcha:
    def __init__(self, client_key):
        self.client = Client(client_key, 28521, debug=False)

    def get_balance(self):
        return self.client.get_balance()

    # def get_gRecaptchaResponse(self, website_url, website_key):
    #     """
    #     :param website_url: 请求的Reference中的内容，一般为项目网站域名
    #     :param website_key: 项目方在recaptcha的key，使用它给用户发recaptcha，出现在iframe的src属性的k参数中
    #     """
    #     task = NoCaptchaTaskProxyless(website_url, website_key)
    #     job = self.client.create_task(task)
    #     gRecaptchaResponse = job.get_solution_recaptcha_response()
    #     return gRecaptchaResponse

    # def get_TurnstileTaskS2(self, website_url, website_key, proxy):
    #     task = TurnstileTaskS2(website_url, website_key, proxy)
    #     job = self.client.create_task(task)
    #     solution = job.get_solution()
    #     token = solution["token"]
    #     user_agent = solution["user_agent"]
    #     return (token, user_agent)

    def get(
        self,
        task: BaseTask,
        token_key: str = "gRecaptchaResponse",
        ua_key: str = "userAgent",
    ) -> tuple[str, str]:  # [token,ua]
        job = self.client.create_task(task)
        solution = job.get_solution()
        token = solution[token_key]
        user_agent = ua_key and solution[ua_key]

        return [token, user_agent]

    def pass_(self, website_url, website_key, driver):
        gRecaptchaResponse: str = self.get_gRecaptchaResponse(website_url, website_key)
        callback: str = driver.execute_script(self.get_js_func())
        func2 = f"{callback}('{gRecaptchaResponse}')"
        driver.execute_script(func2)

    @staticmethod
    def get_js_func():
        return """
function findRecaptchaClients() {
  // eslint-disable-next-line camelcase
  if (typeof (___grecaptcha_cfg) !== 'undefined') {
    // eslint-disable-next-line camelcase, no-undef
    return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
      const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
      const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

      objects.forEach(([toplevelKey, toplevel]) => {
        const found = Object.entries(toplevel).find(([_, value]) => (
          value && typeof value === 'object' && 'sitekey' in value && 'size' in value
        ));
     
        if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
            data.pageurl = toplevel.baseURI;
        }
        
        if (found) {
          const [sublevelKey, sublevel] = found;

          data.sitekey = sublevel.sitekey;
          const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
          const callback = sublevel[callbackKey];
          if (!callback) {
            data.callback = null;
            data.function = null;
          } else {
            data.function = callback;
            const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
            data.callback = `___grecaptcha_cfg.clients${keys}`;
          }
        }
      });
      return data;
    });
  }
  return [];
}

return findRecaptchaClients()[0]['callback']
"""

    def get_js_func_callback():
        return "findRecaptchaClients()[0][callback]"

    @staticmethod
    def get_js(gRecaptchaResponse: str) -> str:
        # https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/9077039/reCaptcha
        # https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/12746875/reCaptcha#1、搜索关键词anchor

        return (
            f"""
gRecaptchaResponse = '{gRecaptchaResponse}'

'"""
            + """'

function findRecaptchaClients() {
  // eslint-disable-next-line camelcase
  if (typeof (___grecaptcha_cfg) !== 'undefined') {
    // eslint-disable-next-line camelcase, no-undef
    return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
      const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
      const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

      objects.forEach(([toplevelKey, toplevel]) => {
        const found = Object.entries(toplevel).find(([_, value]) => (
          value && typeof value === 'object' && 'sitekey' in value && 'size' in value
        ));
     
        if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
            data.pageurl = toplevel.baseURI;
        }
        
        if (found) {
          const [sublevelKey, sublevel] = found;

          data.sitekey = sublevel.sitekey;
          const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
          const callback = sublevel[callbackKey];
          if (!callback) {
            data.callback = null;
            data.function = null;
          } else {
            data.function = callback;
            const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
            data.callback = `___grecaptcha_cfg.clients${keys}`;
          }
        }
      });
      return data;
    });
  }
  return [];
}

eval(findRecaptchaClients()[0]['callback'])(gRecaptchaResponse);

"""
        )
