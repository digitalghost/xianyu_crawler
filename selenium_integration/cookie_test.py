import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import logging
import json
from pprint import pprint

# Main Process Start
if not sys.platform.startswith('win'):
    import coloredlogs
    coloredlogs.install(level='INFO')
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Create a new instance of the Firefox driver
driver = webdriver.Firefox("./")
#driver.implicitly_wait(3600)
driver._is_remote = False
driver.get("https://login.taobao.com/member/login.jhtml?f=top&redirectURL=https%3A%2F%2F2.taobao.com%2F")

# Page 1: input region select and wait human to input the code
logging.info("Load Page Title :%s",driver.title)
logging.info("***SCRIPT***WAIT HUMAN INPUT VCODE***")

element = WebDriverWait(driver, 2600).until(
                EC.visibility_of_element_located((By.ID, 'J_HeaderSearchQuery'))
            )
pprint(driver.get_cookies())


