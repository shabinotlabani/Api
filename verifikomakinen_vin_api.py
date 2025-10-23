from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import requests, zipfile, io, os, time

app = Flask(__name__)

CHROME_PATH = "/tmp/chrome/chrome-linux64/chrome"
CHROME_ZIP_URL = "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.85/linux64/chrome-linux64.zip"


def ensure_chrome_installed():
    """Shkarkon Chromium nëse mungon"""
    if not os.path.exists(CHROME_PATH):
        os.makedirs("/tmp/chrome", exist_ok=True)
        r = requests.get(CHROME_ZIP_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("/tmp/chrome")
        os.chmod(CHROME_PATH, 0o755)


@app.route("/")
def home():
    return "✅ VerifikoMakinen API (me Chrome Portable) është aktiv!"


@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin")
    if not vin:
        return jsonify({"error": "Mungon parametri VIN"}), 400

    try:
        # Sigurohu që Chromium ekziston
        ensure_chrome_installed()

        # Instalo automatikisht Chromedriver
        chromedriver_autoinstaller.install()

        chrome_options = Options()
        chrome_options.binary_location = CHROME_PATH
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        driver.get(url)

        time.sleep(10)  # pritje që faqja të ngarkohet
        vin_input = driver.find_element("id", "carbodynum")
        vin_input.clear()
        vin_input.send_keys(vin)

        search_button = driver.find_element("css selector", "button.btn.btn-black")
        search_button.click()

        time.sleep(20)  # pritje për rezultat
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
