import scrapy
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0


class LoginSpider(scrapy.Spider):
    name = 'login'
    def start_requests(self):
        # Create a new instance of the Firefox driver
        timeout = 3600
        driver = webdriver.Firefox("./")
        driver._is_remote = False
        driver.get("https://login.taobao.com/member/login.jhtml?f=top&redirectURL=https%3A%2F%2F2.taobao.com%2F")

        self.logger.info("Load Page Title :%s",driver.title)
        self.logger.info("***SCRIPT***WAIT HUMAN INPUT VCODE***")
        elm_btn_x = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, 'J_Quick2Static'))
            )
        elm_btn_x.click()
        elm_ipt_x = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, 'TPL_username_1'))
            )
        elm_ipt_x.send_keys('digitalghost1983')
        elm_ipt_x = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, 'TPL_password_1'))
            )
        elm_ipt_x.send_keys('snowsoft')
        elm_btn_x = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, 'J_SubmitStatic'))
            )
        elm_btn_x.click()
        element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.ID, 'J_HeaderSearchQuery'))
            )
        cookies_dict = driver.get_cookies()
        yield scrapy.Request(url='https://2.taobao.com/item.htm?spm=2007.1000337.16.4.RKXgow&id=547844424990',cookies=cookies_dict)
        driver.quit()


    def parse(self, response):
        print response.body

