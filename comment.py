from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Chrome headless option
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Sharhlar sahifasini ochish
url = "https://sharh.commeta.uz/en/reviews/all"
driver.get(url)
time.sleep(5)  # Sahifa yuklanishini kutish

# Scroll qilish orqali barcha sharhlarni yuklash
SCROLL_PAUSE_TIME = 3
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Ma'lumotlarni yig'ish
review_elements = driver.find_elements(By.XPATH, '//div[@itemtype="https://schema.org/Review"]')

data = []
for elem in review_elements:
    try:
        name = elem.find_element(By.XPATH, './/span[@itemprop="name"]').text.strip()
    except:
        name = ''

    try:
        text = elem.find_element(By.XPATH, './/span[@itemprop="reviewBody"]').text.strip()
    except:
        text = ''

    try:
        rating = elem.find_element(By.XPATH, './/meta[@itemprop="ratingValue"]').get_attribute("content")
    except:
        rating = ''

    try:
        date = elem.find_element(By.XPATH, './/meta[@itemprop="datePublished"]').get_attribute("content")
    except:
        date = ''

    data.append({
        'Name': name,
        'Review': text,
        'Rating': rating,
        'Date': date
    })

driver.quit()

# CSV faylga yozish
df = pd.DataFrame(data)
df.to_csv('reviews.csv', index=False, encoding='utf-8')

print(f"✅ {len(data)} ta sharh saqlandi → reviews.csv")
