from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

# 🔧 Chrome-ni headless rejimda sozlash
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

url = "https://sharh.commeta.uz/en/reviews/all"
driver.get(url)
time.sleep(5)

# 📜 Sahifani pastga scroll qilib barcha sharhlarni yuklash
SCROLL_PAUSE_TIME = 3
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 📦 Sharhlar elementlarini yig‘ish
reviews = driver.find_elements(By.XPATH, '//div[@itemtype="https://schema.org/Review"]')
data = []

for review in reviews:
    try:
        user = review.find_element(By.XPATH, './/span[@itemprop="name"]').text.strip()
    except:
        user = ''

    try:
        object_name = review.find_element(By.XPATH, './/p[contains(text(), "Left a review")]/a').text.strip()
    except:
        object_name = ''

    try:
        review_text = review.find_element(By.XPATH, './/span[@itemprop="reviewBody"]').text.strip()
    except:
        review_text = ''

    try:
        rating_value = review.find_element(By.XPATH, './/meta[@itemprop="ratingValue"]').get_attribute('content')
    except:
        rating_value = ''

    try:
        date = review.find_element(By.XPATH, './/meta[@itemprop="datePublished"]').get_attribute('content')
    except:
        date = ''

    try:
        likes = review.find_element(By.XPATH, './/div[contains(text(),"people liked")]').text.strip().split(' ')[0]
    except:
        likes = '0'

    try:
        partial_url = review.get_attribute('id')
        url_address = f"https://sharh.commeta.uz/en/review/{partial_url}"
        url_id = f"/review/{partial_url}"
    except:
        url_address = ''
        url_id = ''

    data.append({
        'user': user,
        'object_name': object_name,
        'review_text': review_text,
        'rating_value': rating_value,
        'date': date,
        'likes': likes,
        'url_address': url_address,
        'url_id': url_id
    })

driver.quit()

# 📁 CSV faylga saqlash
df = pd.DataFrame(data)
df.to_csv("reviews.csv", index=False, encoding='utf-8-sig')

print(f"✅ {len(df)} ta sharh saqlandi → reviews.csv")
