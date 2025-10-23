from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

def kontrollo_vinin(vin):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.carhistory.or.kr/search/carhistory/freeSearch.car?lang=en")
        time.sleep(3)

        vin_input = driver.find_element(By.ID, "carbodynum")
        vin_input.clear()
        vin_input.send_keys(vin)

        search_btn = driver.find_element(By.CLASS_NAME, "btn-black")
        search_btn.click()
        time.sleep(6)

        html = driver.page_source.lower()

        if "no history on the flood damage" in html:
            result = "Nuk ka histori dëmtimi (Flood Damage: No)"
            status = "no_flood"
        elif "flood damage" in html:
            result = "Është gjetur histori dëmtimi (Flood Damage: Yes)"
            status = "flood"
        else:
            result = "Nuk u gjet përgjigje e qartë — kontrollo manualisht"
            status = "unknown"

        return {"success": True, "vin": vin, "status": status, "result": result}

    except Exception as ex:
        return {"success": False, "vin": vin, "error": str(ex)}

    finally:
        driver.quit()


@app.route("/api/check-vin", methods=["GET", "POST"])
def check_vin():
    if request.method == "POST":
        vin = request.get_json().get("vin")
    else:
        vin = request.args.get("vin")

    if not vin:
        return jsonify({"success": False, "message": "VIN nuk u dërgua."}), 400

    print(f"🔎 Kontrollohet VIN: {vin}")
    result = kontrollo_vinin(vin)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
