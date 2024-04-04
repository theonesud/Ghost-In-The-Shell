import os
from time import sleep

import requests
from pypdf import PdfReader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

run_headless = False

url = "https://www.mca.gov.in/mcafoportal/showCheckFilingStatus.do"
driver = None
driver_call_counter = 0
raw_folder = os.path.join(os.getcwd(), "raw")
os.makedirs(raw_folder, exist_ok=True)
CIN = "U24246KA1982PTC021796"


def get_driver():
    global driver, driver_call_counter
    # TODO: check how frequently mca blocks us
    if driver_call_counter % 100 == 0:
        if driver:
            print(".... Quitting driver ....")
            driver.quit()
            driver_call_counter = 0
        if run_headless:
            from selenium.webdriver.firefox.options import Options

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            print(".... Creating Firefox Driver ....")
            driver = webdriver.Firefox(options=options)
            driver.set_page_load_timeout(10)
        else:
            from selenium.webdriver.chrome.options import Options

            print(".... Creating Chrome Driver ....")
            chrome_options = Options()
            chrome_options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": raw_folder,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True,
                    "plugins.always_open_pdf_externally": True,
                },
            )
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(10)
    driver_call_counter += 1
    return driver


def download_pdf():
    driver = get_driver()
    driver.get(url)
    cin_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "companyID"))
    )
    cin_input.clear()
    cin_input.send_keys(CIN)
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "submitBtn"))
    )
    submit_button.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pageNavPosition"))
    )
    last_button = driver.find_element(By.ID, "last")
    # TODO: check cases where there is only one page
    # TODO: check cases where there are no results
    if "pg-nav-inactive" not in last_button.get_attribute("class"):
        last_button.click()
    else:
        print("The 'Last' button is inactive.")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "results")))
    rows = driver.find_elements(
        By.XPATH, "//table[@id='results']//tr[@class='table-row']"
    )
    # TODO: ask team what does it mean if event date / download button is not available
    # TODO: get latest mgt7/7a / aoc (if mgt not available)
    visible_rows = [row for row in rows if row.is_displayed()]
    last_row = visible_rows[-1]
    # TODO: check if download link is available, otherwise get previous one
    download_link = last_row.find_element(
        By.XPATH, ".//td/a[contains(text(), 'Download')]"
    )
    driver.execute_script("arguments[0].click();", download_link)
    sleep(5)  # Wait for the file to download
    original_file_path = os.path.join(raw_folder, "viewChallan.do")
    new_file_path = os.path.join(raw_folder, f"{CIN}.pdf")
    os.rename(original_file_path, new_file_path)
    driver.quit()


def read_pdf():
    with open(os.path.join(raw_folder, f"{CIN}.pdf"), "rb") as file:
        reader = PdfReader(file)
        page = reader.pages[0]
        text = page.extract_text()
        text = text.lower()
        financial_year = text.split("financial year ending on")[1].split()[0]
        return financial_year


if __name__ == "__main__":
    download_pdf()
    # financial_year = read_pdf()
    # print(financial_year)
