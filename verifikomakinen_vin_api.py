from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import time

app = Flask(__name__)

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin", "")
    try:
        # ✅ instalon automatikisht versionin e saktë të ChromeDriver
        driver_path = chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # 🚀 përdor Selenium Manager për të shkarkuar Chromium automatikisht
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        driver.get("https://www.carhistory.or.kr/search/carhistory/freeSearch.car")

        time.sleep(7)  # pritje që faqja të ngarkohet plotësisht
        html = driver.page_source
        driver.quit()

        return jsonify({"vin": vin, "status": "OK", "html_length": len(html)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
