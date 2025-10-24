from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# ✅ Lejon kërkesa nga faqja zyrtare dhe localhost gjatë testimit
CORS(app, origins=[
    "https://verifikomakinen.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5173",   # vite / react / blazor dev servers
    "https://localhost:7071"   # Blazor WebAssembly me HTTPS
])

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "VerifikoMakinen API eshte aktiv!"})


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
        session.post("https://www.carhistory.or.kr/main.car",
                     data={"lang": "en"}, headers=headers, timeout=10)
        session.cookies.set("search_agree", "Y", domain="www.carhistory.or.kr")

        url = "https://www.carhistory.or.kr/search/carhistory/freeSearch.car"
        data = {"carnum": vin, "lang": "en"}
        response = session.post(url, headers=headers, data=data, timeout=20)

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        # Analizo tekstin
        if "error in the vin" in text:
            result = "❌ Numri VIN eshte i pasakte."
        elif "no history on the flood damage accident" in text:
            result = "✅ Nuk ka histori permbytjeje ne Korene e Jugut."
        elif "flood" in text or "damage" in text:
            result = "⚠️ Ka histori permbytjeje."
        else:
            result = "ℹ️ Nuk u gjet informacion i qarte."

        return jsonify({
            "vin": vin,
            "result": result,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
