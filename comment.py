import time
import os
import pickle
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException

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

# ✅ Checkpoint yuklash
loaded_ids = set()
if os.path.exists(pkl_file):
    with open(pkl_file, 'rb') as f:
        loaded_ids = pickle.load(f)
    print(f"♻️ Oldindan yuklangan {len(loaded_ids)} ta sharh mavjud.")

# 🔄 Sahifani ochish
driver.get(url)
time.sleep(5)

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

        except Exception as e:
            continue

    return extracted

# 🔁 Barcha sharhlar uchun aylanish
all_data = []

while True:
    print("🔄 Yangi sharhlar qidirilmoqda...")
    new_reviews = extract_reviews()

    if not new_reviews:
        print("❌ Yangi sharh topilmadi.")
    else:
        print(f"✅ {len(new_reviews)} ta yangi sharh topildi.")
        all_data.extend(new_reviews)

        # CSV ga qo‘shib yozish
        df = pd.DataFrame(new_reviews)
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # Checkpoint saqlash
        with open(pkl_file, 'wb') as f:
            pickle.dump(loaded_ids, f)

    try:
        load_more_btn = driver.find_element(By.XPATH, '//span[contains(text(), "Load more")]')
        driver.execute_script("arguments[0].click();", load_more_btn)
        time.sleep(1.5)
    except NoSuchElementException:
        print("✅ Barcha sharhlar yuklandi.")
        break
    except ElementClickInterceptedException:
        print("⚠️ Load More tugmasini bosib bo‘lmadi, qaytadan urinib ko‘riladi...")
        time.sleep(2)
    except Exception as e:
        print("❌ Xatolik:", str(e))
        break

driver.quit()
