from flask import Flask, request, jsonify
import undetected_chromedriver as uc
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ VerifikoMakinen API është aktiv dhe gati për kërkesa VIN."

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin")
    if not vin:
        return jsonify({"error": "Mungon parametri VIN"}), 400

    try:
        # Krijon Chrome driver automatikisht, pa kërkuar binary të sistemit
        driver = uc.Chrome(headless=True)

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        driver.get(url)
        time.sleep(3)

        vin_input = driver.find_element("id", "carbodynum")
        vin_input.clear()
        vin_input.send_keys(vin)

        search_button = driver.find_element("css selector", "button.btn.btn-black")
        search_button.click()
        time.sleep(5)

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
