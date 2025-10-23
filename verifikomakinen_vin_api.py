from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ VerifikoMakinen API është aktiv (me pritje inteligjente)."

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin")
    if not vin:
        return jsonify({"error": "Mungon parametri VIN"}), 400

    try:
        chromedriver_autoinstaller.install()

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 30)  # pret deri në 30 sekonda

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        driver.get(url)

        # pret që inputi të jetë i gatshëm (derisa ngarkohet faqa)
        vin_input = wait.until(EC.presence_of_element_located((By.ID, "carbodynum")))
        vin_input.clear()
        vin_input.send_keys(vin)

        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-black")))
        search_button.click()

        # pret që rezultati të shfaqet (ose maksimumi 20 sekonda)
        time.sleep(20)

        page = driver.page_source.lower()
        driver.quit()

        if "no history on the flood damage" in page:
            result = "Nuk ka histori dëmi nga përmbytja."
        elif "flood" in page:
            result = "Mund të ketë histori përmbytjeje."
        else:
            result = "Rezultati nuk u përcaktua."

        return jsonify({"vin": vin, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
