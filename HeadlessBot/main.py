from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string
import time
#import undetected_chromedriver as uc

page = "feedback-1"
URL = f"https://study-dev.ru/{page}"

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

def run():
    #options = uc.ChromeOptions()

    #options = uc.ChromeOptions()

    #options.user_data_dir = r"C:\Users\makce\AppData\Local\Google\Chrome\User Data"

    #options.add_argument(r"--profile-directory=Profile 3")
    #options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_argument("--window-size=800,600")
    #options.headless = False

    #driver = uc.Chrome(options=options)


    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1200,900")

    driver = webdriver.Chrome(options=chrome_options)


    try:
        driver.get(URL)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        #time.sleep(random.uniform(1.0, 3.0))
        time.sleep(random.uniform(0.0, 10.0))

        form = driver.find_element(By.TAG_NAME, "form")
        fields = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")

        for f in fields:
            fill_field(f)
            #time.sleep(random.uniform(0.2, 0.7))

        if page == "feedback-2":
            try:
                WebDriverWait(driver, 15).until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.CSS_SELECTOR, 'iframe[src*="recaptcha/api2/anchor"]')
                    )
                )

                checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
                )
                
                checkbox.click()
                # driver.execute_script("arguments[0].click();", checkbox)

                print("[OK] Чекбокс reCAPTCHA кликнут")
                driver.switch_to.default_content()
                #time.sleep(random.uniform(6.9, 10.0))

                driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[src*="recaptcha/api2/anchor"]'))
                is_checked = driver.find_element(By.ID, "recaptcha-anchor").get_attribute("aria-checked") == "true"
                driver.switch_to.default_content()
                
                if is_checked:
                    print("[OK] Капча пройдена")
                else:
                    print("[WARN] Капча НЕ отмечена — возможно, потребуются картинки")

            except Exception as e:
                print(f"[ERROR] Проблема с reCAPTCHA: {e}")

        if page == "feedback-3":
            try:
                print("[INFO] Обработка Cloudflare Turnstile (visible checkbox mode)...")

                turnstile_host = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".cf-turnstile"))
                )
                print("[OK] cf-turnstile контейнер найден")

                get_iframe_script = """
                function getTurnstileIframe() {
                    let host = document.querySelector('.cf-turnstile');
                    if (!host) return null;
                    
                    // Пытаемся достать shadow root (closed не всегда доступен, но в Turnstile часто работает через children)
                    let shadow = host.shadowRoot;
                    if (!shadow) {
                        // fallback: ищем внутри первого div после host
                        let inner = host.querySelector('div');
                        if (inner) shadow = inner.shadowRoot;
                    }
                    if (!shadow) return null;
                    
                    // Ищем iframe по src или id-паттерну
                    let iframe = shadow.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                                shadow.querySelector('iframe[id^="cf-chl-widget-"]') ||
                                shadow.querySelector('iframe[title*="Cloudflare"]');
                    return iframe;
                }
                let iframe = getTurnstileIframe();
                return iframe ? {id: iframe.id, src: iframe.src} : null;
                """

                iframe_info = driver.execute_script(get_iframe_script)

                if iframe_info and iframe_info.get('id'):
                    iframe_id = iframe_info['id']
                    print(f"[OK] iframe найден, id: {iframe_id}")

                    WebDriverWait(driver, 10).until(
                        EC.frame_to_be_available_and_switch_to_it((By.ID, iframe_id))
                    )
                    print("[OK] Переключились в Turnstile iframe")

                    checkbox = WebDriverWait(driver, 12).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "label.cb-lb, input[type='checkbox']"))
                    )

                    driver.execute_script("arguments[0].click();", checkbox)
                    print("[OK] Чекбокс 'Подтвердите, что вы человек' кликнут")

                    WebDriverWait(driver, 15).until(
                        lambda d: d.find_element(By.ID, "success").is_displayed()
                    )
                    print("[SUCCESS] Проверка пройдена (success видим)")

                    driver.switch_to.default_content()

                else:
                    print("[WARN] iframe не найден через JS → возможно другой режим или детект")

                #time.sleep(random.uniform(5, 10))

                token = driver.execute_script(
                    "return document.querySelector('input[name=\"cf-turnstile-response\"]').value;"
                )
                if token and len(token) > 40:
                    print("[SUCCESS] Токен получен")
                else:
                    print("[WARN] Токен не получен")

            except Exception as e:
                print(f"[ERROR] Turnstile обработка: {type(e).__name__} - {str(e)}")
                driver.save_screenshot("turnstile_fail.png")
        #time.sleep(random.uniform(30, 60))
        try:
            submit = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
            #time.sleep(0.4)
            
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

        #time.sleep(2)
        print("Успешно отправлено. URL:", driver.current_url)

    finally:
        driver.quit()

run()