from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin", "").strip()
    if not vin:
        return jsonify({"error": "VIN mungon"}), 400

    try:
        # Simulo kërkesë si përdorues browseri
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        data = {"carbodynum": vin, "lang": "en"}

        # Dërgo kërkesën
        response = requests.post(url, headers=headers, data=data, timeout=15)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Lexo rezultatet bazë (mund ta rafinojmë më vonë)
        result_text = soup.get_text().strip()[:300]

        return jsonify({
            "vin": vin,
            "result": "Data u mor me sukses",
            "preview": result_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
