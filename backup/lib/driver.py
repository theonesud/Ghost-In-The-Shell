import random
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

driver = None
driver_call_counter = 0


def get_driver():
    global driver, driver_call_counter
    if driver_call_counter % 80 == 0:
        if driver:
            print(".... Quitting driver ....")
            driver.quit()
            print(".... Cooling down for 2 mins to avoid suspicion ....")
            time.sleep(120)
            driver_call_counter = 0
        print(".... Creating driver ....")
        driver = webdriver.Chrome()
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)
    driver_call_counter += 1
    return driver


def scroll_to_bottom(driver, wait_time=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for new content to load
        time.sleep(wait_time)

        # Calculate new scroll height and compare with the last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


def get_url(url, retries=3, timeout=30):
    driver = get_driver()
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(3)
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            break
        except TimeoutException:
            if attempt < retries - 1:
                print(f"Retrying... (Attempt {attempt + 2}/{retries})")
            else:
                raise TimeoutException("Page failed to load after multiple attempts")
    time.sleep(random.uniform(1, 10))
    return driver.page_source
