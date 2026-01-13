import time
import schedule
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from companies import TARGET_COMPANIES
from keywords import BLACKLIST, GOLDLIST_JOBS, DATE_KEYWORDS, LOCATIONS

# --- CONFIGURATION TELEGRAM ---
# J'ai mis ton token ici.
TELEGRAM_TOKEN = "8041098189:AAGNgMa1abXsvNGtcgW0mwdpeah-bofkvmA"

# ⚠️ REMPLACE LE 0 CI-DESSOUS PAR LE NUMÉRO QUE TU AS TROUVÉ DANS LE LIEN
TELEGRAM_CHAT_ID = "5233378719" 

HISTORY_FILE = "history.txt"

def send_telegram(message):
    """Envoie le message sur Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ Erreur Telegram: {response.text}")
        else:
            print("✅ Message envoyé !")
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")

def calculate_score(title, company, description, location):
    score = 5 
    
    # 1. Kill Switch
    for bad_word in BLACKLIST:
        if bad_word.lower() in title.lower():
            return 0 

    # 2. Company Bonus
    for target in TARGET_COMPANIES:
        if target.lower() in company.lower():
            score += 3
            break
    
    # 3. Job Type Bonus
    for gold_word in GOLDLIST_JOBS:
        if gold_word.lower() in title.lower():
            score += 2
            break
            
    # 4. Date Bonus
    for date_word in DATE_KEYWORDS:
        if date_word.lower() in description.lower():
            score += 1
            break

    # 5. Filtre Luxembourg
    if "luxembourg" in location.lower() and score < 7:
        return 0 

    return score

def scrape_job_board():
    print("🔄 Lancement du scraping...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Erreur driver: {e}")
        return

    # --- SIMULATION DE DONNÉES (TEST) ---
    mock_jobs = [
        {"title": "Stage Sales Asset Management", "company": "Amundi", "loc": "Paris", "desc": "Début Mai", "link": "http://amundi.com/job1"},
        {"title": "Stage Private Equity", "company": "Tikehau", "loc": "Paris", "desc": "Avril 2026", "link": "http://tikehau.com/job2"},
    ]

    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, "w").close()
    
    with open(HISTORY_FILE, "r") as f:
        history = f.read()

    for job in mock_jobs:
        if job['link'] in history:
            print(f"Déjà vu: {job['company']}")
            continue

        score = calculate_score(job['title'], job['company'], job['desc'], job['loc'])
        
        if score >= 6: 
            emoji = "🔥" if score >= 8 else "✅"
            msg = (
                f"{emoji} *Nouvelle Offre ({score}/10)*\n\n"
                f"🏢 *Boite:* {job['company']}\n"
                f"💼 *Poste:* {job['title']}\n"
                f"📍 *Lieu:* {job['loc']}\n"
                f"🔗 [Lien]({job['link']})"
            )
            
            send_telegram(msg)
            
            with open(HISTORY_FILE, "a") as f:
                f.write(job['link'] + "\n")
                
    driver.quit()

# Test immédiat
scrape_job_board()

# Planification
schedule.every().day.at("09:00").do(scrape_job_board)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
