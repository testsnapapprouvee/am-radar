import time
import schedule
import os
import requests
import shutil
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from companies import TARGET_COMPANIES
from keywords import BLACKLIST, GOLDLIST_JOBS, DATE_KEYWORDS, LOCATIONS

# --- IDENTIFIANTS TELEGRAM ---
TELEGRAM_TOKEN = "8041098189:AAGNgMa1abXsvNGtcgW0mwdpeah-bofkvmA"
TELEGRAM_CHAT_ID = "5233378719"

HISTORY_FILE = "history.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
        print("✅ Message Telegram envoyé !")
    except Exception as e:
        print(f"❌ Erreur connexion Telegram : {e}")

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
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # --- DÉTECTION ROBUSTE DU SYSTÈME ---
    system_os = platform.system()
    print(f"🖥️ Système détecté : {system_os}")

    if system_os == "Linux":
        # On est sur Railway
        print("🐧 Mode Linux/Railway activé.")
        
        # 1. Chercher Chrome sous plusieurs noms
        chrome_path = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        # 2. Chercher le Driver
        chromedriver_path = shutil.which("chromedriver")

        if chrome_path and chromedriver_path:
            print(f"✅ Binaires trouvés :\n   Chrome: {chrome_path}\n   Driver: {chromedriver_path}")
            chrome_options.binary_location = chrome_path
            service = Service(executable_path=chromedriver_path)
        else:
            print("⚠️ ATTENTION : Binaires non trouvés via 'which'. Recherche dans /usr/bin...")
            # Tentative de forçage si 'which' échoue
            if os.path.exists("/usr/bin/chromium"):
                chrome_options.binary_location = "/usr/bin/chromium"
                service = Service("/usr/bin/chromedriver")
                print("✅ Binaires forcés via /usr/bin")
            else:
                print("❌ CRITIQUE : Chrome introuvable sur le serveur.")
                return
    else:
        # On est sur ton Mac/PC
        print("💻 Mode Local (Mac/Windows).")
        try:
            service = Service(ChromeDriverManager().install())
        except Exception as e:
            print(f"❌ Erreur installation driver local: {e}")
            return
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("🚀 Navigateur lancé avec succès !")
    except Exception as e:
        print(f"❌ CRASH DRIVER (Erreur fatale): {e}")
        return

    # --- LE RESTE NE CHANGE PAS ---
    mock_jobs = [
        {"title": "Stage Sales Asset Management", "company": "Amundi", "loc": "Paris", "desc": "Début Mai", "link": "http://amundi.com/job-test-final"},
        {"title": "Stage Private Equity", "company": "Tikehau", "loc": "Paris", "desc": "Avril 2026", "link": "http://tikehau.com/job-test-final"},
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
            emoji = "🔥" if score >= 8 else "✅"
            msg = (
                f"{emoji} *Bot Actif ({score}/10)*\n\n"
                f"🏢 {job['company']}\n"
                f"💼 {job['title']}\n"
                f"📍 {job['loc']}\n"
                f"🔗 [Voir l'offre]({job['link']})"
            )
            
            send_telegram(msg)
            
            with open(HISTORY_FILE, "a") as f:
                f.write(job['link'] + "\n")
                
    driver.quit()
    print("✅ Scraping terminé.")

# Lancement au démarrage
scrape_job_board()

schedule.every().day.at("09:00").do(scrape_job_board)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
