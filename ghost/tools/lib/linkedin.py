import os
import pickle
import random
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from lib.driver import get_driver, get_url

os.makedirs("scrapes/linkedin", exist_ok=True)


def search_linkedin(keyword):
    driver = get_driver()
    driver.get("https://www.linkedin.com/")

    # Wait until the search bar is present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
    )

    # Now that we are sure that the search bar is there, find it and enter the keyword
    search_bar = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
    search_bar.clear()
    search_bar.send_keys(keyword)
    search_bar.send_keys(Keys.RETURN)

    # Wait until the search results are loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(@class, 'search-results-container')]")
        )  # Adjust XPATH based on actual results container
    )


def download_plp_pages():
    """Gets a list of founders in US for fashion and accessories industries."""
    os.makedirs("scrapes/linkedin/plp", exist_ok=True)
    for word in [
        "founder",
        "ceo",
        "entrepreneur",
        "startup",
        "owner",
        # "president",
        # "chairman",
    ]:
        for page_no in range(1, 11):
            url = f"https://www.linkedin.com/search/results/people/?geoUrn=%5B%22103644278%22%5D&industry=%5B%22615%22%2C%2219%22%5D&keywords={word}&origin=FACETED_SEARCH&page={page_no}&sid=sTd"
            try:
                _, source = get_url(url)
                with open(f"scrapes/linkedin/plp/{word}_{page_no}.html", "w") as f:
                    f.write(source)
            except TimeoutException:
                print(f"Timeout: {url}")


def get_pdp_links():
    """Extracts profile links from the downloaded listing pages."""
    unique_profiles = set()
    for file in os.listdir("scrapes/linkedin/plp"):
        if file.endswith(".html"):
            with open(f"scrapes/linkedin/plp/{file}") as f:
                html = f.read()
                soup = BeautifulSoup(html, "html.parser")
                links = soup.find_all("a", class_="app-aware-link")
                profile_links = [link["href"] for link in links if "href" in link.attrs]
                profile_links = [
                    link for link in profile_links if "miniProfile" in link
                ]
                unique_profiles.update(profile_links)
    with open("scrapes/linkedin/unique_profiles.pkl", "wb") as f:
        pickle.dump(unique_profiles, f)


def download_pdp_pages():
    os.makedirs("scrapes/linkedin/pdp", exist_ok=True)
    with open("scrapes/linkedin/unique_profiles.pkl", "rb") as f:
        unique_profiles = pickle.load(f)
    for profile_link in unique_profiles:
        profile_id = profile_link.split("?")[0].split("/")[-1]
        if os.path.exists(f"scrapes/linkedin/pdp/{profile_id}.html"):
            continue
        try:
            source = get_url(f"https://www.linkedin.com/in/{profile_id}/")
            with open(f"scrapes/linkedin/pdp/{profile_id}.html", "w") as f:
                f.write(source)
        except TimeoutException:
            print(f"Timeout: {profile_id}")


def extract_profile_info():
    for file in os.listdir("scrapes/linkedin/pdp"):
        if file.endswith(".html"):
            with open(f"scrapes/linkedin/pdp/{file}") as f:
                html = f.read()
                soup = BeautifulSoup(html, "html.parser")
                print(soup)
        break
