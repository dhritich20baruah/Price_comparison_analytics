from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import time
import random
import csv
import re
from supabase import create_client
import datetime

load_dotenv()

SUPABASE_URL = "https://knptwhyychjbrfdeaerx.supabase.co"
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver.get(f"https://www.nike.com/ph/w")

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

time.sleep(180)

wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__body"))
)

products = []
products = driver.find_elements(By.CLASS_NAME, "product-card__body")
print(f"{len(products)} items found")

def php_to_inr(price_text):
    numeric = price_text.replace("₱", "").replace(",", "").strip()
    try:
        php_value = float(numeric)
        inr_value = round(php_value * 1.56, 2)
        return inr_value
    except:
        return "N/A"

def discount_percent(original, current):
    if original == "N/A" or current == "N/A" or original == 0:
        return 0
    return round(((original - current) / original) * 100, 2)

all_products = []

for product in products:
    try:       
        Name = product.find_element(By.CLASS_NAME, "product-card__link-overlay").text
        URL = product.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay").get_attribute("href")
        Image_URL = product.find_element(By.TAG_NAME, "img").get_attribute("src")
        price_wrapper = product.find_element(By.CSS_SELECTOR, ".product-price__wrapper")
        aria = price_wrapper.get_attribute("aria-label")
        curr = re.search(r"current price ([₱\d,]+)", aria)
        orig = re.search(r"original price ([₱\d,]+)", aria)
        if curr:
            current_price = curr.group(1)
        if orig:
            original_price = orig.group(1)

        Discount_Price = php_to_inr(current_price)
        Original_Price = php_to_inr(original_price)

        Discount_Percentage = discount_percent(Original_Price, Discount_Price)

        all_products.append({
            "URL": URL, 
            "Image_URL": Image_URL, 
            "Name": Name, 
            "Original_Price": Original_Price, 
            "Discount_Price": Discount_Price, 
            "Discount_Percentage": Discount_Percentage
            })

    except Exception as e:
        print("Listing error: ", e)

driver.quit()

with open("product_listings.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "URL", 
        "Image_URL", 
        "Name", 
        "Original_Price(INR)", 
        "Discount_Price(INR)", 
        "Discount_Percentage"
    ])

    for p in all_products:
        writer.writerow([
            p["URL"], 
            p["Image_URL"], 
            p["Name"], 
            p["Original_Price"], 
            p["Discount_Price"], 
            p["Discount_Percentage"]
        ])

def upsert_product(product):
    response = supabase.table("products").upsert(
        {
        "product_url": product["URL"],
        "product_name": product["Name"],
        "product_image_url": product["Image_URL"]
        },
        on_conflict="product_url"
    ).execute()

    if not response.data:
        raise Exception("Product upsert failed")

    return response.data[0]["id"]

def insert_price_history(product_id, product):
    response = supabase.table("price_history").insert(
        {
            "product_id": product_id,
            "original_price_inr": product["Original_Price"],
            "discount_price_inr": product["Discount_Price"],
            "discount_percent": product["Discount_Percentage"],
            "scraped_at": datetime.datetime.now(datetime.UTC).isoformat()
        }
    ).execute()

    return response

for product in all_products:
    product_id = upsert_product(product)
    insert_price_history(product_id, product)

print("Data saved to ecommerce_product_sample.csv")