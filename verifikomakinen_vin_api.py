from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os, time

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ VerifikoMakinen API është aktiv me Chromium!"

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin")
    if not vin:
        return jsonify({"error": "Mungon parametri VIN"}), 400

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.binary_location = "/usr/bin/chromium-browser"  # vendosim rrugën për Render

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        driver.get(url)
        time.sleep(3)

        vin_input = driver.find_element("id", "carbodynum")
        vin_input.clear()
        vin_input.send_keys(vin)

        search_button = driver.find_element("css selector", "button.btn.btn-black")
        search_button.click()
        time.sleep(5)

        body_text = driver.page_source

        if "no history on the flood damage" in body_text.lower():
            result = "Nuk ka histori dëmi nga përmbytja."
        elif "flood" in body_text.lower():
            result = "Mund të ketë histori përmbytjeje."
        else:
            result = "Rezultati nuk u përcaktua saktë."

        driver.quit()
        return jsonify({"vin": vin, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
