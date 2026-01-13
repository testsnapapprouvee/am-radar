import time
import schedule
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
# On utilise CallMeBot pour faire simple (pas besoin de compte Twilio payant/complexe)
import requests 
from companies import TARGET_COMPANIES
from keywords import BLACKLIST, GOLDLIST_JOBS, DATE_KEYWORDS, LOCATIONS

# --- CONFIGURATION ---
# Sur Railway, ces variables seront dans les "Variables d'environnement"
PHONE_NUMBER = os.getenv("PHONE_NUMBER") # Ton numéro avec format international (ex: 33600...)
API_KEY = os.getenv("API_KEY") # Ta clé CallMeBot

HISTORY_FILE = "history.txt"

def send_whatsapp(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={message}&apikey={API_KEY}"
    try:
        requests.get(url)
        print("✅ Notification envoyée !")
    except Exception as e:
        print(f"❌ Erreur envoi WhatsApp: {e}")

def calculate_score(title, company, description, location):
    score = 5 # Base score pour "Stage Asset Mgmt"
    
    # 1. Check Blacklist (Kill Switch)
    for bad_word in BLACKLIST:
        if bad_word.lower() in title.lower():
            return 0 # Offre rejetée

    # 2. Check Company (Le gros bonus)
    is_top_tier = False
    for target in TARGET_COMPANIES:
        if target.lower() in company.lower():
            score += 3
            is_top_tier = True
            break
    
    # 3. Check Job Type
    for gold_word in GOLDLIST_JOBS:
        if gold_word.lower() in title.lower():
            score += 2
            break
            
    # 4. Check Date
    for date_word in DATE_KEYWORDS:
        if date_word.lower() in description.lower():
            score += 1
            break

    # 5. Filtre Luxembourg (Doit être une top offre)
    if "luxembourg" in location.lower() and score < 7:
        return 0 # On ignore les offres moyennes au Lux

    return score

def scrape_job_board():
    print("🔄 Lancement du scraping...")
    
    # Setup Chrome pour serveur (Headless)
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Installation auto du driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # --- URL CIBLE (Exemple Indeed ou eFinancialCareers) ---
    # Note: Ceci est un exemple générique. 
    # Pour un vrai scrape, il faut cibler une URL précise et adapter les sélecteurs CSS.
    url = "https://www.efinancialcareers.fr/jobs/Asset_Management/in_Paris?q=Stage"
    try:
        driver.get(url)
        time.sleep(5)
        
        # Simulation récupération d'offres (A REMPLACER PAR VRAI SELECTEUR)
        # jobs = driver.find_elements(By.CLASS_NAME, "job-card") 
        
        # --- DONNÉES DE TEST POUR VALIDER LA LOGIQUE ---
        # Une fois le bot en place, on remplacera ça par le vrai scraping
        mock_jobs = [
            {"title": "Stage Sales Asset Management", "company": "Amundi", "loc": "Paris", "desc": "Début Mai", "link": "http://amundi.com"},
            {"title": "Internship Compliance", "company": "BlackRock", "loc": "London", "desc": "Start May", "link": "http://blackrock.com/compliance"}, # Devrait être rejeté (Blacklist)
            {"title": "Stage Private Equity", "company": "Tikehau", "loc": "Paris", "desc": "Avril 2026", "link": "http://tikehau.com"},
            {"title": "Assistant Gestion", "company": "Banque Inconnue", "loc": "Luxembourg", "desc": "Mai", "link": "http://unknown.com"} # Devrait être rejeté (Score faible Lux)
        ]

        # Chargement historique
        if not os.path.exists(HISTORY_FILE):
            open(HISTORY_FILE, "w").close()
        
        with open(HISTORY_FILE, "r") as f:
            history = f.read()

        for job in mock_jobs:
            if job['link'] in history:
                continue

            score = calculate_score(job['title'], job['company'], job['desc'], job['loc'])
            
            if score >= 6: # On notifie seulement si score décent
                emoji = "🔥" if score >= 8 else "✅"
                msg = (
                    f"{emoji} *Nouvelle Offre ({score}/10)*\n"
                    f"🏢 {job['company']}\n"
                    f"💼 {job['title']}\n"
                    f"📍 {job['loc']}\n"
                    f"🔗 {job['link']}"
                )
                # Encodage URL pour WhatsApp
                encoded_msg = requests.utils.quote(msg)
                send_whatsapp(encoded_msg)
                
                # Sauvegarde pour ne pas renvoyer
                with open(HISTORY_FILE, "a") as f:
                    f.write(job['link'] + "\n")

    except Exception as e:
        print(f"Erreur scraping: {e}")
    finally:
        driver.quit()

# Planification : Tous les jours à 09h00
schedule.every().day.at("09:00").do(scrape_job_board)

# Pour tester tout de suite au lancement du script :
scrape_job_board() 

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
