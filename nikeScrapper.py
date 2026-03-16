from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import csv
import re
import requests
import datetime

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver.get(f"https://www.nike.in/men/men-s-shoes/c/92564")

SCROLL_SPEED = 10     
SCROLL_INTERVAL = 5

driver.execute_script(f"""
    const scrollStep = {SCROLL_SPEED};
    const scrollInterval = {SCROLL_INTERVAL};

    let totalHeight = 0;
    const timer = setInterval(() => {{
        window.scrollBy(0, scrollStep);
        totalHeight += scrollStep;

        if (totalHeight >= document.body.scrollHeight) {{
            clearInterval(timer);
        }}
    }}, scrollInterval);
""")

time.sleep(10)

wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1mbp38s"))
)

products = []
products = driver.find_elements(By.CLASS_NAME, "css-1mbp38s")
print(f"{len(products)} items found")

# def php_to_inr(price_text):
#     numeric = price_text.replace("₱", "").replace(",", "").strip()
#     try:
#         php_value = float(numeric)
#         inr_value = round(php_value * 1.56, 2)
#         return inr_value
#     except:
#         return "N/A"

all_products = []

for product in products:
    try:       
        Name = product.find_element(By.CLASS_NAME, "css-12xgt1").text
        URL = product.find_element(By.CSS_SELECTOR, "a.css-1o8jw7q").get_attribute("href")
        Image_URL = product.find_element(By.TAG_NAME, "img").get_attribute("src")
  
        disount = product.find_elements(By.CLASS_NAME, "css-6k8kzr")
        if disount:
            Discount_Price = disount[0].text
        else:
            Discount_Price = "NA"    

        Original_Price =  product.find_element(By.TAG_NAME, "h3").text

        all_products.append({
            "URL": URL, 
            "Image_URL": Image_URL, 
            "Name": Name, 
            "Original_Price": Original_Price, 
            "Discount_Price": Discount_Price
            })
        print(all_products)
        break

    except Exception as e:
        print("Listing error: ", e)

# for i, product in enumerate(all_products):
#     print(f"Scraping product {i+1}/{len(all_products)}")

#     driver.get(product["URL"])
#     time.sleep(random.uniform(2.5, 4))

#     # Description
#     try:
#         Product_Description = driver.find_element(By.ID, 'product-description-container').text
#         product["Description"] = Product_Description
#     except:
#         product["Description"] = "N/A"

driver.quit()

# with open("nike_shoes.csv", "w", newline="", encoding="utf-8") as f:
#     writer = csv.writer(f)
#     writer.writerow([
#         "URL", 
#         "Image_URL", 
#         "Name", 
#         "Original_Price(INR)", 
#         "Discount_Price(INR)", 
#     ])

#     for p in all_products:
#         writer.writerow([
#             p["URL"], 
#             p["Image_URL"], 
#             p["Name"], 
#             p["Original_Price"], 
#             p["Discount_Price"], 
#         ])

print("Data saved to ecommerce_product_sample.csv")