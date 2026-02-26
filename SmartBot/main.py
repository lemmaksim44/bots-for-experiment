from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random
import string
import time
import os

page = "feedback-2"
URL = f"http://localhost:8000/{page}"

def rand_text(n=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def is_visible_and_enabled(el):
    try:
        return el.is_displayed() and el.is_enabled()
    except:
        return False

def fill_field(element):
    tag = element.tag_name.lower()
    ftype = (element.get_attribute("type") or "").lower()
    name = element.get_attribute("name")

    if ftype == "hidden":
        return
    if not is_visible_and_enabled(element):
        print(f"[skip] {name} not interactable")
        return

    try:
        if tag == "input":
            if ftype == "email":
                element.send_keys(rand_text(6) + "@bot.net")
            elif ftype in ["submit", "button"]:
                return
            else:
                element.send_keys(rand_text(random.randint(6, 20)))

        elif tag == "textarea":
            element.send_keys(rand_text(random.randint(10, 50)))

        elif tag == "select":
            options = element.find_elements(By.TAG_NAME, "option")
            if options:
                options[random.randint(0, len(options)-1)].click()

        print(f"[fill] {name}")

    except Exception as e:
        print(f"[error] {name}: {e}")

def wait_captcha_solved(driver, timeout=300):
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(By.CSS_SELECTOR, ".captcha-solver")
                    .get_attribute("data-state") in ("success", "solved", "done")
    )
    print("Капча решена")

def run():
    options = Options()
    user_data_path = r"C:\Users\makce\Desktop\bot-profile"

    options.add_argument(f"--user-data-dir={user_data_path}")
    options.add_argument("--profile-directory=Profile 3")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--remote-debugging-pipe")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(URL)

        wait_captcha_solved(driver, timeout=120)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        time.sleep(random.uniform(1.0, 3.0))

        form = driver.find_element(By.TAG_NAME, "form")
        fields = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")

        for f in fields:
            fill_field(f)
            time.sleep(random.uniform(0.2, 0.7))

        try:
            submit = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
            time.sleep(0.4)
            
            try:
                submit.click()
                print("Обычный клик")
            except Exception as e:
                driver.execute_script("arguments[0].click();", submit)
                print("JS-клик")
                
        except Exception as e:
            print(f"[ERROR] Не смогли найти кнопку submit: {e}")
            
            try:
                form = driver.find_element(By.TAG_NAME, "form")
                driver.execute_script("arguments[0].submit();", form)
                print("[FORCED] Форма отправлена через form.submit()")
            except:
                print("[FAIL] Принудительный submit не сработал")

        time.sleep(2)
        print("Успешно отправлено. URL:", driver.current_url)

    finally:
        driver.quit()

run()