import time
import schedule
import os
import requests
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from companies import TARGET_COMPANIES
from keywords import BLACKLIST, GOLDLIST_JOBS, DATE_KEYWORDS, LOCATIONS

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8041098189:AAGNgMa1abXsvNGtcgW0mwdpeah-bofkvmA"
TELEGRAM_CHAT_ID = "5233378719"
HISTORY_FILE = "history_v2.txt" # On garde la V2 pour l'instant

# LISTE ATS
ATS_DOMAINS = [
    "myworkdayjobs.com", "successfactors.eu", "tal.net", 
    "jobs.amundi.com", "groupgti.com", "taleo.net", "smartrecruiters.com"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except Exception as e: print(f"❌ Erreur Telegram : {e}")

def get_driver():
    """Configuration renforcée anti-détection"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080") # Important pour voir les éléments
    # User Agent d'un vrai PC Windows récent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def process_job(title, company, location, link, source, description_snippet=""):
    # Nettoyage
    link = link.split('?')[0]
    title = title.strip() if title else "Titre Inconnu"
    company = company.strip() if company else "Entreprise Inconnue"
    
    print(f"   🔎 ANALYSE: [{title}] chez [{company}]")

    # 1. Historique
    if not os.path.exists(HISTORY_FILE): open(HISTORY_FILE, "w").close()
    with open(HISTORY_FILE, "r") as f: history = f.read()
    
    if link in history:
        print("      -> 🛑 Déjà traité")
        return

    # 2. Blacklist
    for bad_word in BLACKLIST:
        if bad_word.lower() in title.lower():
            print(f"      -> 🛑 Blacklisté: '{bad_word}'")
            return

    # 3. Localisation (Souple)
    loc_ok = False
    full_text_check = (location + " " + title + " " + description_snippet).lower()
    
    for loc in LOCATIONS:
        if loc.lower() in full_text_check:
            loc_ok = True; break
    
    if "suisse" in full_text_check or "zurich" in full_text_check or "geneva" in full_text_check:
        loc_ok = True

    # Si c'est une boite cible, on ignore la loc
    is_target = False
    for target in TARGET_COMPANIES:
        if target.lower() in company.lower() or target.lower() in title.lower(): 
            is_target = True; break

    if not loc_ok and not is_target:
        print(f"      -> 🛑 Mauvaise loc: {location}")
        return 

    # 4. Scoring
    score = 5
    if is_target: score += 3
    for gold in GOLDLIST_JOBS:
        if gold.lower() in title.lower(): score += 2; break
    for date in DATE_KEYWORDS:
        if date.lower() in description_snippet.lower(): score += 1; break

    # ENVOI
    if score >= 6:
        print(f"      -> 🔥 SUCCÈS ({score}/10) !")
        emoji = "🔥" if score >= 8 else "✅"
        msg = f"{emoji} *{source} ({score}/10)*\n🏢 {company}\n💼 {title}\n📍 {location}\n🔗 [Voir l'offre]({link})"
        send_telegram(msg)
        with open(HISTORY_FILE, "a") as f: f.write(link + "\n")
    else:
        print(f"      -> 📉 Note trop basse ({score}/10)")

# --- JOBTEASER (CORRIGÉ) ---
def scrape_jobteaser():
    print("running: JobTeaser...")
    driver = get_driver()
    try:
        url = "https://www.jobteaser.com/fr/job-offers?query=Asset+Management&contract=internship"
        driver.get(url)
        time.sleep(5)
        # On cherche plus large pour éviter les erreurs
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job-offers/']")
        print(f"JobTeaser: {len(links)} liens bruts trouvés.")
        
        for i, link_elem in enumerate(links):
            try:
                link = link_elem.get_attribute("href")
                # On ne filtre plus sur le texte vide, on prend tout
                raw_text = link_elem.text.replace("\n", " | ")
                
                # Extraction basique
                title = "Offre JobTeaser"
                company = "Inconnue"
                
                if raw_text:
                    parts = raw_text.split("|")
                    title = parts[0].strip()
                    if len(parts) > 1: company = parts[1].strip()
                
                process_job(title, company, "France/Europe", link, "JobTeaser")
            except Exception as e:
                print(f"   ⚠️ Erreur lien {i}: {e}")
                continue
    except Exception as e: print(f"Erreur Globale JT: {e}")
    finally: driver.quit()

# --- X-RAY ATS (CORRIGÉ) ---
def scrape_ats_xray():
    print("running: X-Ray ATS...")
    driver = get_driver()
    search_locations = ' OR '.join([f'"{loc}"' for loc in LOCATIONS[:4]])
    
    try:
        for ats in ATS_DOMAINS:
            print(f"   🔎 Scan de {ats}...")
            search_query = f'site:{ats} "Asset Management" ("Stage" OR "Internship") ({search_locations})'
            # On passe par DuckDuckGo HTML (plus permissif que Bing/Google)
            url = f"https://html.duckduckgo.com/html/?q={search_query}"
            driver.get(url)
            time.sleep(5)
            
            # Sélecteur DuckDuckGo
            results = driver.find_elements(By.CLASS_NAME, "result__body")
            print(f"   -> {len(results)} résultats.")
            
            for res in results:
                try:
                    title_elem = res.find_element(By.CLASS_NAME, "result__a")
                    title = title_elem.text
                    link = title_elem.get_attribute("href")
                    
                    company = "Boite Directe"
                    if "amundi" in link: company = "Amundi"
                    elif "pictet" in link: company = "Pictet"
                    elif "-" in title: company = title.split("-")[-1].strip()

                    process_job(title, company, "Site Carrière", link, f"X-Ray ({ats})")
                except: continue
    except Exception as e: print(f"Erreur X-Ray: {e}")
    finally: driver.quit()

# --- WTTJ (Simplifié) ---
def scrape_wttj():
    print("running: WTTJ...")
    driver = get_driver()
    try:
        url = "https://www.welcometothejungle.com/fr/jobs?query=Asset%20Management&refinementList%5Bcontract_type%5D%5B%5D=internship&aroundQuery=Paris"
        driver.get(url)
        time.sleep(8) # Plus de temps pour charger
        cards = driver.find_elements(By.TAG_NAME, "article")
        print(f"WTTJ: {len(cards)} trouvés.")
        for card in cards:
            try:
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                text = card.text.split("\n")
                title = text[0] if text else "Titre WTTJ"
                company = text[1] if len(text)>1 else "Boite WTTJ"
                process_job(title, company, "Paris", link, "WTTJ")
            except: continue
    except: pass
    finally: driver.quit()

# --- INDEED SUISSE ---
def scrape_indeed_ch():
    print("running: Indeed CH...")
    driver = get_driver()
    try:
        url = "https://ch.indeed.com/jobs?q=Asset+Management&l=Switzerland&sc=0kf%3Ajt%28internship%29%3B"
        driver.get(url)
        time.sleep(5)
        cards = driver.find_elements(By.CLASS_NAME, "resultContent")
        print(f"Indeed: {len(cards)} trouvés.")
        for card in cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h2").text
                link = card.find_element(By.XPATH, "./ancestor::tr").find_element(By.TAG_NAME, "a").get_attribute("href")
                process_job(title, "Indeed Company", "Suisse", link, "Indeed CH")
            except: continue
    except: pass
    finally: driver.quit()

def run_all():
    print("🚀 Démarrage DEBUG...")
    scrape_jobteaser() # On commence par celui qui avait 22 liens
    time.sleep(3)
    scrape_ats_xray()
    time.sleep(3)
    scrape_wttj()
    time.sleep(3)
    scrape_indeed_ch()
    print("✅ Fin DEBUG.")

schedule.every(4).hours.do(run_all)
run_all()

if __name__ == "__main__":
    while True: schedule.run_pending(); time.sleep(60)
