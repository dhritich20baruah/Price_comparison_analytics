from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 10)

product_links = ["https://www.nike.com/ph/t/mercurial-superfly-10-elite-air-max-95-se-high-top-football-boot-cnkFbV/HV9916-001"]

for i, url in enumerate(product_links):
    print(f"Scraping product {i+1}/{len(product_links)}")

    driver.get(url)
    time.sleep(random.uniform(2, 4))

    # Description
    try:
        Product_Description = driver.find_element(By.ID, 'product-description-container').text
    except:
        Product_Description = "N/A"

    print(Product_Description)

driver.quit()