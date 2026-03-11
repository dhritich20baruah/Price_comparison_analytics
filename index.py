from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import csv

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

time.sleep(300)

wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__body"))
)

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

product_links = []
all_data = []
for product in products:
    try:
        has_discount = len(product.find_elements(By.CSS_SELECTOR, "[data-testid='product-price-reduced']")) > 0

        # ---------- CONDITION 2: HAS "RECYCLED MATERIALS" TAG ----------
        is_recycled = False
        try:
            tag_text = product.find_element(By.CSS_SELECTOR, "[data-testid='product-card__messaging']").text
            if "Recycled" in tag_text:
                is_recycled = True
        except:
            pass
        if has_discount and is_recycled:
            Product_Name = product.find_element(By.TAG_NAME, "a").get_attribute("href")
            Product_URL = product.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay").get_attribute("href")
            Product_Image_URL = product.find_element(By.TAG_NAME, "img").get_attribute("src")
            current_price = product.find_element(By.CSS_SELECTOR, "[data-testid='product-price-reduced']").text
            original_price = product.find_element(By.CSS_SELECTOR, "[data-testid='product-price']").text
            Discount_Price = php_to_inr(current_price)
            Original_Price = php_to_inr(original_price)
            product_links.append(Product_URL)

            all_data.append([Product_URL, Product_Image_URL, Product_Name, Original_Price, Discount_Price])
    except:
        pass

with open("ecommerce_product_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Product_URL", "Product_Image_URL", "Product_Name", "Original_Price", "Discount_Price", "Product_Description", "Voucher", "Sizes_Available", "Available_Colors", "Color_Shown", "Style_Code", "Rating_Score", "Review_Count"])
    writer.writerows(all_data)

for i, url in enumerate(product_links):
    print(f"Scraping product {i+1}/{len(product_links)}")

    driver.get(url)
    time.sleep(random.uniform(2, 4))

    # Description
    try:
        Product_Description = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-description"]').text
    except:
        Product_Description = "N/A"

    # Sizes
    sizes_available_arr = []

    try:
        wait.until(EC.presence_of_element_located((By.ID, "size-selector")))
        size_buttons = driver.find_elements(By.CSS_SELECTOR, "#size-selector button")

        for btn in size_buttons:
            if btn.is_enabled():
                sizes_available_arr.append(btn.text.strip())

    except:
        pass

    Sizes_Available = ", ".join(sizes_available_arr) if sizes_available_arr else "N/A"

    try:
        Voucher = driver.find_element(By.CSS_SELECTOR, "[data-testid='OfferPercentage']").text
    except:
        Voucher = "N/A"

    available_colors = []

    try:
        color_buttons = driver.find_elements(By.CSS_SELECTOR, "[data-testid='colorway-picker-container'] button")

        for color in color_buttons:
            label = color.get_attribute("aria-label")
            if label:
                available_colors.append(label)

    except:
        pass

    Available_Colors = ", ".join(available_colors) if available_colors else "N/A"

    try:
        Color_Shown = driver.find_element(
            By.XPATH,
            "//li[contains(@data-testid,'color-description')]"
        ).text.replace("Colour Shown:", "").strip()
    except:
        Color_Shown = "N/A"

    try:
        Style_Code = driver.find_element(
            By.XPATH,
            "//li[contains(@data-testid,'style-color')]"
        ).text.replace("Style:", "").strip()
    except:
        Style_Code = "N/A"

    try:
        Rating_Score = driver.find_element(By.CSS_SELECTOR, "[data-testid='review-summary-rating']").get_attribute("title")
    except:
        Rating_Score = "No rating"

    try:
        Review_Count = driver.find_element(By.CSS_SELECTOR, "[data-testid='reviews-summary']").text
        Review_Count = ''.join(filter(str.isdigit, Review_Count))
    except:
        Review_Count = "0"

    all_data.append([Product_URL, Product_Image_URL, Product_Name, Original_Price, Discount_Price, Product_Description, Voucher, Sizes_Available, Available_Colors, Color_Shown, Style_Code, Rating_Score, Review_Count])

driver.quit()

with open("nike_scraper.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Product_URL", "Product_Image_URL", "Product_Name", "Original_Price", "Discount_Price", "Product_Description", "Voucher", "Sizes_Available", "Available_Colors", "Color_Shown", "Style_Code", "Rating_Score", "Review_Count"])
    writer.writerows(all_data)

print("Data saved to nike_products.csv")