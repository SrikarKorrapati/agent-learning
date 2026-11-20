from selenium import webdriver
from selenium.webdriver.common.by import By

with webdriver.Chrome() as browser:
    browser.get("https://www.selenium.dev/selenium/web/web-form.html")

    text_box = browser.find_element(By.NAME, "my-text")
    text_box.send_keys("Hello from Python!")

    submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    confirmation = browser.find_element(By.ID, "message").text
    print(confirmation)
    assert confirmation == "Received!"
