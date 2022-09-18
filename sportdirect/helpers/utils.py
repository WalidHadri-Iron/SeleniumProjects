from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import FirefoxProfile
import helpers.constants as cs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import helpers.xpaths as xpaths
from helpers.custom_exceptions import _NotFoundException
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(process)-4s %(message)s ',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')



def build_driver(chrome=True):
    if chrome:
        # options = webdriver.ChromeOptions()
        # options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--incognito")
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(executable_path=cs.CHROME_DRIVER_PATH)
    else:
        #options = Options()
        #options.headless = True
        driver = webdriver.Firefox(executable_path=cs.FIREFOX_DRIVER_PATH)
    return driver


def get_main_url_to_close_pop_up(_driver):
    _d = _driver
    _d.get(cs.MAIN_URL)
    try:
        button = wait_visible_xpath(_d, xpaths.COUNTRY_POP_UP_CLOSE_BUTTON)
        #button.click()
        ActionChains(_d).move_to_element(button).click(button).perform()
    except _NotFoundException:
        logging.info("It seems that the close button of the country popup has not been found")


# wait x seconds for the visibility of the element to be found by xpath
# if found, return it
# if not, catch the TimeoutException and raise _NotFoundException
def wait_visible_xpath(driver, xpath, seconds=2.0):
    try:
        wait_ = WebDriverWait(driver, seconds)
        return wait_.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        raise _NotFoundException


# wait x seconds for the visibility of the elements to be found by xpath
# if found, return them
# if not, catch the TimeoutException and raise _NotFoundException
def wait_presents_xpath(driver, xpath, seconds=0.5):
    try:
        wait_ = WebDriverWait(driver, seconds)
        return wait_.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    except TimeoutException:
        raise _NotFoundException


# use wait_visible_xpath to return the text if found
# else catch _NotFoundException and return blank text
def get_text_xpath(driver, xpath, seconds=0.1):
    try:
        return wait_visible_xpath(driver, xpath, seconds).text
    except _NotFoundException:
        logging.info(f"The text of xpath={xpath} was not found!")
        return ""


# find the first span child text of a selenium element
def elem_to_span_child_text(driver, _elem):
    try:
        #span_element = _elem.find_element(by=By.TAG_NAME, value='span')
        print(driver.current_url)
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        span_element = WebDriverWait(driver, 2,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located(By.TAG_NAME))
        span_element = _elem.find_element(by=By.TAG_NAME, value='span')
        return span_element.text
    except NoSuchElementException:
        logging.error(f"The element {_elem} doesn't have a span child")
        return ""


# description cleaning
def clean_description(_desc):
    # remove prohibited text
    for p_text in cs.DESCRIPTION_PROHIBITED_TEXTS:
        _desc.replace(p_text, '')
    # remove urls
    _desc = re.sub(cs.URL_REGEX, '', _desc)
    # remove duplicate whitespaces
    _desc = re.sub(' +', ' ', _desc)
    return _desc
