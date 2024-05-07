import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Firefox()
driver.get('https://voxukraine.org/tag/voxcheck')

i = 2

while i < 2000:
    try:
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                f'/html/body/main/section[2]/div/div/div[2]/div[{i}]/button'
            ))
        )
        load_more_button.click()
        i += 1
    except Exception as e:
        print(e)
        break

df = pd.DataFrame(columns=['text'])

elements = driver.find_elements(By.TAG_NAME, 'article')
for el in elements:
    title = el.find_element(By.TAG_NAME, 'h2')
    df = df._append({'text': title.text}, ignore_index=True)

df.to_csv('new_data.csv', index=False)
