import os
import pickle
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
import random
import time
from datetime import datetime

# 🔧 Chrome sozlamalar
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# 📂 Fayl nomlari
csv_file = "reviews.csv"
pkl_file = "checkpoint.pkl"

# 🌍 URL
url = "https://sharh.commeta.uz/en/reviews/all"

# ✅ Checkpointdan yuklash
loaded_ids = set()
current_page = 1
if os.path.exists(pkl_file):
    with open(pkl_file, 'rb') as f:
        checkpoint_data = pickle.load(f)
        loaded_ids = checkpoint_data.get("ids", set())
        current_page = checkpoint_data.get("page", 1)
    print(f"{datetime.now()} ♻️ Oldindan yuklangan {len(loaded_ids)} ta sharh mavjud. Sahifa: {current_page}")

# 🔄 Saytni ochish
driver.get(url)
time.sleep(5)

# ➕ Avvalgi sahifalarni yuklash
for _ in range(current_page - 1):
    try:
        load_more_btn = driver.find_element(By.XPATH, '//span[contains(text(), "Load more")]')
        driver.execute_script("arguments[0].click();", load_more_btn)
        time.sleep(random.uniform(1.5, 3.5))
    except Exception:
        break

# 🧩 Sharhlarni olish funksiyasi
def extract_reviews():
    reviews = driver.find_elements(By.XPATH, '//div[@itemtype="https://schema.org/Review"]')
    extracted = []
    for review in reviews:
        try:
            review_id = review.get_attribute("id")
            if review_id in loaded_ids:
                continue

            user = review.find_element(By.XPATH, './/span[@itemprop="name"]').text.strip()
            object_name = review.find_element(By.XPATH, './/p[contains(text(), "Left a review")]/a').text.strip()
            review_text = review.find_element(By.XPATH, './/span[@itemprop="reviewBody"]').text.strip()
            rating_value = review.find_element(By.XPATH, './/meta[@itemprop="ratingValue"]').get_attribute('content')
            date = review.find_element(By.XPATH, './/meta[@itemprop="datePublished"]').get_attribute('content')
            likes = review.find_element(By.XPATH, './/div[contains(text(),"people liked")]').text.strip().split(' ')[0]
            url_address = f"https://sharh.commeta.uz/en/review/{review_id}"
            url_id = f"/review/{review_id}"

            extracted.append({
                'user': user,
                'object_name': object_name,
                'review_text': review_text,
                'rating_value': rating_value,
                'date': date,
                'likes': likes,
                'url_address': url_address,
                'url_id': url_id
            })

            loaded_ids.add(review_id)
        except Exception:
            continue
    return extracted

# 🔁 Sahifalar bo‘yicha aylanish
all_data = []

while True:
    print(f"{datetime.now()} 🔄 Yangi sharhlar qidirilmoqda... Sahifa: {current_page}")
    new_reviews = extract_reviews()

    if not new_reviews:
        print(f"{datetime.now()} ❌ Yangi sharh topilmadi.")
    else:
        print(f"{datetime.now()} ✅ {len(new_reviews)} ta yangi sharh topildi.")
        all_data.extend(new_reviews)

        df = pd.DataFrame(new_reviews)
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # 🔐 Checkpoint saqlash
        with open(pkl_file, 'wb') as f:
            pickle.dump({"ids": loaded_ids, "page": current_page}, f)

    try:
        load_more_btn = driver.find_element(By.XPATH, '//span[contains(text(), "Load more")]')
        driver.execute_script("arguments[0].click();", load_more_btn)
        time.sleep(random.uniform(3, 6))
        current_page += 1
    except NoSuchElementException:
        print(f"{datetime.now()} ✅ Barcha sharhlar yuklandi.")
        break
    except ElementClickInterceptedException:
        print(f"{datetime.now()} ⚠️ Load More tugmasini bosib bo‘lmadi, yana urinilmoqda...")
        time.sleep(random.uniform(3, 6))
    except Exception as e:
        print(f"{datetime.now()} ❌ Xatolik yuz berdi: {e}")
        break

driver.quit()
