import requests
from bs4 import BeautifulSoup
import random
import string

URL = "http://127.0.0.1:8000/feedback-1/"

def rand_text(n=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def gen_value_by_type(field):
    ftype = field.get("type", "text")

    if ftype == "hidden":
        return None

    if field.get("value"):
        return field.get("value")

    if ftype in ["checkbox", "radio"]:
        return field.get("value", "on")

    if ftype == "email":
        return rand_text(6) + "@bot.net"

    # textarea / text / password / search и т.п.
    return rand_text(random.randint(6, 20))

def run():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": URL
    }

    r_get = session.get(URL, headers=headers)
    print("GET status:", r_get.status_code)

    soup = BeautifulSoup(r_get.text, "html.parser")
    form = soup.find("form")
    if not form:
        print("Форма не найдена")
        return

    data = {}

    csrf_input = form.find("input", {"name": "csrfmiddlewaretoken"})
    if csrf_input:
        data["csrfmiddlewaretoken"] = csrf_input.get("value")

    for field in form.find_all(["input", "textarea", "select"]):
        name = field.get("name")
        if not name or name == "csrfmiddlewaretoken":
            continue

        value = gen_value_by_type(field)
        if value is not None:
            data[name] = value

    # POST сессией
    r_post = session.post(URL, data=data, headers=headers)
    print("POST status:", r_post.status_code)
    print("Payload:", data)

run()