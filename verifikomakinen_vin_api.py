from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ VerifikoMakinen API është aktiv (Render Chrome portable)."

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin")
    if not vin:
        return jsonify({"error": "Mungon parametri VIN"}), 400

    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # Mos vendos binary_location — uc e menaxhon vetë
        driver = uc.Chrome(options=options, use_subprocess=True)

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        driver.get(url)
        time.sleep(3)

        vin_input = driver.find_element("id", "carbodynum")
        vin_input.clear()
        vin_input.send_keys(vin)

        search_button = driver.find_element("css selector", "button.btn.btn-black")
        search_button.click()
        time.sleep(5)

        body = driver.page_source.lower()
        driver.quit()

        if "no history on the flood damage" in body:
            result = "Nuk ka histori dëmi nga përmbytja."
        elif "flood" in body:
            result = "Mund të ketë histori përmbytjeje."
        else:
            result = "Rezultati nuk u përcaktua."

        return jsonify({"vin": vin, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
