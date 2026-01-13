import time
import schedule
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from companies import TARGET_COMPANIES
from keywords import BLACKLIST, GOLDLIST_JOBS, DATE_KEYWORDS, LOCATIONS

# --- TES INFOS ---
TELEGRAM_TOKEN = "8041098189:AAGNgMa1abXsvNGtcgW0mwdpeah-bofkvmA"
TELEGRAM_CHAT_ID = "5233378719"
HISTORY_FILE = "history.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
        print("✅ Message Telegram envoyé !")
    except Exception as e:
        print(f"❌ Erreur Telegram : {e}")

def calculate_score(title, company, description, location):
    score = 5 
    for bad_word in BLACKLIST:
        if bad_word.lower() in title.lower(): return 0 
    for target in TARGET_COMPANIES:
        if target.lower() in company.lower(): score += 3; break
    for gold_word in GOLDLIST_JOBS:
        if gold_word.lower() in title.lower(): score += 2; break
    for date_word in DATE_KEYWORDS:
        if date_word.lower() in description.lower(): score += 1; break
    if "luxembourg" in location.lower() and score < 7: return 0 
    return score

def scrape_job_board():
    print("🔄 Lancement du scraping...")
    
    # Configuration Chrome Spécifique Docker
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # ICI : On pointe directement vers les fichiers installés par le Dockerfile
    # C'est la partie qui change tout.
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("🚀 Navigateur lancé avec succès !")
    except Exception as e:
        print(f"❌ CRASH : {e}")
        return

    # --- TEST RAPIDE ---
    mock_jobs = [
        {"title": "Stage Sales Asset Management", "company": "Amundi", "loc": "Paris", "desc": "Début Mai", "link": "http://amundi.com/final-test"},
        {"title": "Stage Private Equity", "company": "Tikehau", "loc": "Paris", "desc": "Avril 2026", "link": "http://tikehau.com/final-test"},
    ]

    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, "w").close()
    
    with open(HISTORY_FILE, "r") as f:
        history = f.read()

    for job in mock_jobs:
        if job['link'] in history:
            continue

        score = calculate_score(job['title'], job['company'], job['desc'], job['loc'])
        if score >= 6: 
            msg = f"🔥 *Bot Docker OK*\n🏢 {job['company']}\n🔗 [Lien]({job['link']})"
            send_telegram(msg)
            with open(HISTORY_FILE, "a") as f:
                f.write(job['link'] + "\n")
                
    driver.quit()
    print("✅ Scraping terminé.")

# Lancement
scrape_job_board()
schedule.every().day.at("09:00").do(scrape_job_board)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
