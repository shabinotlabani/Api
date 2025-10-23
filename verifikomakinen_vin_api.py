from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/check-vin")
def check_vin():
    vin = request.args.get("vin", "").strip()
    if not vin:
        return jsonify({"error": "VIN mungon"}), 400

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/141.0.0.0 Safari/537.36",
            "Referer": "https://www.carhistory.or.kr/main.car"
        }

        session = requests.Session()

        # 1️⃣ Vendos gjuhën në EN (sikur e ndryshon manualisht)
        session.post(
            "https://www.carhistory.or.kr/main.car",
            data={"lang": "en"},
            headers=headers,
            timeout=10
        )

        # 2️⃣ Simulo klikimin “Agree to all the use of the service”
        session.cookies.set("search_agree", "Y", domain="www.carhistory.or.kr")

        # 3️⃣ Dërgo kërkesën reale për kontrollin e VIN
        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        data = {"carnum": vin, "lang": "en"}
        response = session.post(url, headers=headers, data=data, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        # 4️⃣ Analizo rezultatin sipas tekstit të faqes
        if "no history on the flood damage accident" in text:
            result = "✅ Nuk ka histori përmbytjeje"
        elif "flood" in text:
            result = "⚠️ Ka histori përmbytjeje"
        else:
            result = "ℹ️ Nuk u gjet informacion i qartë"

        return jsonify({
            "vin": vin,
            "result": result,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
