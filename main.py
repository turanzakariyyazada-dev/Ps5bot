import time
import threading
import requests
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8916383180:AAFTvA0IwcvF4czFF1Dukkr8XEC8wYCM50Y"
CHAT_ID = "8617116517"
MIN_QIYMET = 500
MAX_QIYMET = 1100
YOXLAMA_INTERVALLI = 30

URL = "https://tap.az/elanlar?utf8=%E2%9C%93&order=created_at&q%5Bkeywords%5D=playstation+5"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
}

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot aktivdir!")

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), SimpleHandler)
    server.serve_forever()

def telegram_mesaj_gonder(mesaj):
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    try:
        requests.post(send_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Mesaj gonderilmedi: {e}")

def elanlari_yoxla():
    gorulmus_elanlar = set()
    print("Sistem calisir...")
    telegram_mesaj_gonder(
        f"🤖 <b>PS5 & PS5 Slim İzləmə Botu Aktivləşdirildi!</b>\n"
        f"💰 Qiymət aralığı: {MIN_QIYMET} - {MAX_QIYMET} AZN"
    )

    while True:
        try:
            cavab = requests.get(URL, headers=HEADERS, timeout=15)
            if cavab.status_code == 200:
                soup = BeautifulSoup(cavab.text, "html.parser")
                elanlar = soup.find_all("div", class_="products-i")

                for elan in elanlar:
                    link_tag = elan.find("a", class_="products-i__link")
                    if not link_tag:
                        continue

                    elan_id = elan.get("data-id") or link_tag.get("href")
                    elan_link = "https://tap.az" + link_tag.get("href")

                    qiymet_tag = elan.find("span", class_="price-val")
                    ad_tag = elan.find("div", class_="products-i__name")

                    qiymet_metn = qiymet_tag.text.strip().replace(" ", "") if qiymet_tag else "0"
                    ad = ad_tag.text.strip() if ad_tag else "PlayStation 5"

                    try:
                        qiymet = int("".join(filter(str.isdigit, qiymet_metn)))
                    except ValueError:
                        qiymet = 0

                    if elan_id not in gorulmus_elanlar:
                        gorulmus_elanlar.add(elan_id)
                        
                        if MIN_QIYMET <= qiymet <= MAX_QIYMET:
                            mesaj = (
                                f"🔥 <b>YENİ PS5 / SLIM ELANI TAPILDI!</b>\n\n"
                                f"📌 <b>Elan:</b> {ad}\n"
                                f"💰 <b>Qiymət:</b> {qiymet} AZN\n"
                                f"🔗 <b>Link:</b> {elan_link}"
                            )
                            telegram_mesaj_gonder(mesaj)

            time.sleep(YOXLAMA_INTERVALLI)

        except Exception as xeta:
            print(f"Xeta: {xeta}")
            time.sleep(15)

if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    elanlari_yoxla()
