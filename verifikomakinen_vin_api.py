from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ VerifikoMakinen API është aktiv me Chrome portable!"

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin")
    if not vin:
        return jsonify({"error": "Mungon parametri VIN"}), 400

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # Krijo një instance të Chrome që shkarkohet automatikisht
        driver = uc.Chrome(options=chrome_options)

        # Hap faqen koreane
        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        driver.get(url)
        time.sleep(3)

        # Fut VIN
        vin_input = driver.find_element("id", "carbodynum")
        vin_input.clear()
        vin_input.send_keys(vin)

        # Kliko butonin “Search”
        search_button = driver.find_element("css selector", "button.btn.btn-black")
        search_button.click()
        time.sleep(5)

        # Merr tekstin e faqes
        body_text = driver.page_source.lower()

        if "no history on the flood damage" in body_text:
            result = "Nuk ka histori dëmi nga përmbytja."
        elif "flood" in body_text:
            result = "Mund të ketë histori përmbytjeje."
        else:
            result = "Rezultati nuk u përcaktua saktë."

        driver.quit()
        return jsonify({"vin": vin, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
