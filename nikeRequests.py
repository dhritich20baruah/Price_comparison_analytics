import requests

url = "https://www.nike.in/men/men-s-shoes/c/92564"

html_text = requests.get(url).text

with open(f"nike.html", "w", encoding="utf-8") as f:
    f.write(html_text)
