from table3.app_account import Gmail
from util.recaptcha import Recaptcha

from .chrome import MyChrome
from .selenium_ import *


# TODO: 待完善
class Google:
    url = "https://accounts.google.com/ServiceLogin?service=accountsettings&continue=https://myaccount.google.com%3Futm_source%3Daccount-marketing-page%26utm_medium%3Dgo-to-account-button"
    website_url = "https://accounts.google.com/"
    website_key = "6LdD2OMZAAAAAAv2xVpeCk8yMtBtY3EhDWldrBbh"

    @classmethod
    def login(cls, recaptcha: Recaptcha, driver: MyChrome, gmail: Gmail):
        # driver.get(cls.url)

        # 邮箱
        driver.wait_element_located("//input[@type='email']", 10).send_keys(gmail.email)
        # 下一步
        driver.find_element(By.XPATH, "//div[@data-primary-action-label]//button").click()

        # 出现recaotcha(v3)验证
        input_list = driver.find_elements(By.XPATH, "//input")
        if len(input_list) == 2:
            raise Exception("after input email, find recaptcha v3")

        # 密码
        driver.wait_element_clickable("//input[@type='password']", 10).send_keys(gmail.pwd)
        # 下一步
        driver.find_element(By.XPATH, "//div[@data-primary-action-label]//button").click()

        # # recaptcha
        # recaptcha.pass_(cls.website_url, cls.website_key, driver)
        # # 下一步
        # driver.find_element(By.XPATH, "//div[@data-primary-action-label]//button").click()

        driver.wait_element_located("//a[@href='personal-info'] | //div[@data-challengetype]")

        e = driver.find_element_nonable("//div[@data-challengetype='12']")
        if not e:
            return

        # 确认您的辅助邮箱
        # driver.find_element(By.XPATH, "//div[@data-challengetype='12']").click()
        e.click()

        # 辅助邮箱
        driver.find_element(By.XPATH, "//input[@type='email']").send_keys(gmail.additional_mail)

        # 确认
        driver.find_element(By.XPATH, "//div[@data-primary-action-label]//button").click()

    @classmethod
    def choose(cls, driver: MyChrome):
        # 选择（唯一的）账号
        driver.find_element(By.XPATH, "//div[@data-identifier]").click()
        # 点击continue
        btn_list = driver.find_elements(By.XPATH, "//div[@data-is-primary-action-disabled]//button")
        assert len(btn_list) == 2
        btn_true = btn_list[1]
        btn_true.click()

        # 可能需要验证
        btn_continue = driver.find_element_nonable(By.XPATH, "//div[@data-primary-action-label]//button")
        if btn_continue:
            btn_continue.click()
            # cls.verify()

    @staticmethod
    def verify():
        pass
