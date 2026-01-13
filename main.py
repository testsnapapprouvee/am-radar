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
HISTORY_FILE = "history.txt"

# LISTE ATS
ATS_DOMAINS = [
    "myworkdayjobs.com",   # Julius Baer, Franklin Templeton, BlackRock
    "successfactors.eu",   # PICTET
    "tal.net",             # LAZARD
    "jobs.amundi.com",     # AMUNDI
    "groupgti.com",        # DWS
    "taleo.net",           # SocGen, HSBC
    "smartrecruiters.com"  # Divers
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Erreur Telegram : {e}")

def get_driver():
    """Configuration Docker Railway"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    return webdriver.Chrome(service=service, options=chrome_options)

def process_job(title, company, location, link, source, description_snippet=""):
    """Cerveau central : Filtre, Note et Envoie"""
    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, "w").close()
    with open(HISTORY_FILE, "r") as f:
        history = f.read()

    link = link.split('?')[0] # Nettoyage lien
    if link in history: return

    # --- SCORING ---
    score = 5
    
    # 1. Entreprise (+3)
    is_target = False
    for target in TARGET_COMPANIES:
        if target.lower() in company.lower() or target.lower() in title.lower(): 
            score += 3
            is_target = True
            break
            
    # 2. Métier (+2)
    for gold_word in GOLDLIST_JOBS:
        if gold_word.lower() in title.lower(): score += 2; break
        
    # 3. Kill Switch
    for bad_word in BLACKLIST:
        if bad_word.lower() in title.lower(): return
        
    # 4. Filtre Date
    for date_word in DATE_KEYWORDS:
        if date_word.lower() in description_snippet.lower(): score += 1; break

    # 5. Filtre Localisation Strict
    loc_ok = False
    for loc in LOCATIONS:
        if loc.lower() in location.lower() or loc.lower() in title.lower() or loc.lower() in description_snippet.lower():
            loc_ok = True
            break
    
    if "suisse" in location.lower() or "switzerland" in location.lower() or "zurich" in location.lower() or "geneva" in location.lower():
        loc_ok = True

    if not loc_ok and not is_target:
        return 

    # SEUIL D'ENVOI
    if score >= 6:
        emoji = "🔥" if score >= 8 else "✅"
        msg = (
            f"{emoji} *{source} ({score}/10)*\n"
            f"🏢 {company}\n"
            f"💼 {title}\n"
            f"📍 {location}\n"
            f"🔗 [Voir l'offre]({link})"
        )
        send_telegram(msg)
        
        with open(HISTORY_FILE, "a") as f:
            f.write(link + "\n")

# --- MODULE 1 : INDEED SUISSE ---
def scrape_indeed_ch():
    print("running: Indeed Suisse (CH)...")
    driver = get_driver()
    try:
        url = "https://ch.indeed.com/jobs?q=Asset+Management&l=Switzerland&sc=0kf%3Ajt%28internship%29%3B"
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        
        cards = driver.find_elements(By.CLASS_NAME, "resultContent")
        print(f"Indeed CH: {len(cards)} offres trouvées")

        for card in cards:
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                title = title_elem.text
                
                try: company = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                except: company = "Indeed Company"
                
                try: loc = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text
                except: loc = "Suisse"

                link_elem = card.find_element(By.XPATH, "./ancestor::tr").find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
                
                process_job(title, company, loc, link, "Indeed CH")
            except: continue
    except Exception as e:
        print(f"Erreur Indeed CH: {e}")
    finally:
        driver.quit()

# --- MODULE 2 : WELCOME TO THE JUNGLE ---
def scrape_wttj():
    print("running: Welcome to the Jungle...")
    driver = get_driver()
    try:
        url = "https://www.welcometothejungle.com/fr/jobs?query=Asset%20Management&refinementList%5Bcontract_type%5D%5B%5D=internship&aroundQuery=Paris"
        driver.get(url)
        time.sleep(5)
        cards = driver.find_elements(By.TAG_NAME, "article")
        for card in cards:
            try:
                try: title = card.find_element(By.TAG_NAME, "h4").text
                except: title = card.find_element(By.TAG_NAME, "h3").text
                
                # C'EST ICI QUE L'ERREUR ÉTAIT (LIGNE 171)
                company = card.find_element(By.TAG_NAME, "span").text 
                
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                process_job(title, company, "Paris", link, "WTTJ")
            except: continue
    except: pass
    finally: driver.quit()

# --- MODULE 3 : JOBTEASER ---
def scrape_jobteaser():
    print("running: JobTeaser...")
    driver = get_driver()
    try:
        url = "https://www.jobteaser.com/fr/job-offers?query=Asset+Management&contract=internship"
        driver.get(url)
        time.sleep(5)
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job-offers/']")
        for link_elem in links:
            try:
                link = link_elem.get_attribute("href")
                text = link_elem.text
                if not text: continue
                title = text.split('\n')[0]
                company = "JobTeaser Partner" 
                if len(text.split('\n')) > 1: company = text.split('\n')[1]
                process_job(title, company, "Voir Lien", link, "JobTeaser")
            except: continue
    except: pass
    finally: driver.quit()

# --- MODULE 4 : GOOGLE X-RAY (ATS) ---
def scrape_ats_xray():
    print("running: X-Ray ATS...")
    driver = get_driver()
    search_locations = ' OR '.join([f'"{loc}"' for loc in LOCATIONS[:6]]) 
    
    try:
        for ats in ATS_DOMAINS:
            print(f"   🔎 Scan de {ats}...")
            search_query = f'site:{ats} "Asset Management" ("Stage" OR "Internship") ({search_locations})'
            url = f"https://www.bing.com/search?q={search_query}"
            driver.get(url)
            time.sleep(random.uniform(4, 7)) 
            
            results = driver.find_elements(By.CLASS_NAME, "b_algo")
            for res in results:
                try:
                    title_elem = res.find_element(By.TAG_NAME, "h2")
                    title = title_elem.text
                    link = res.find_element(By.TAG_NAME, "a").get_attribute("href")
                    try: snippet = res.find_element(By.CLASS_NAME, "b_caption").text
                    except: snippet = ""
                    
                    company = "Boite Directe"
                    if "amundi" in link: company = "Amundi"
                    elif "pictet" in link or "successfactors" in link: company = "Pictet"
                    elif "tal.net" in link: company = "Lazard"
                    elif "groupgti" in link: company = "DWS"
                    elif "-" in title: company = title.split("-")[-1].strip()

                    process_job(title, company, "Site Carrière", link, f"Direct ({ats})", snippet)
                except: continue
    except: pass
    finally: driver.quit()

# --- ORCHESTRATION ---
def run_all():
    print("🚀 Démarrage complet...")
    scrape_indeed_ch()
    time.sleep(5)
    scrape_wttj()
    time.sleep(5)
    scrape_jobteaser()
    time.sleep(5)
    scrape_ats_xray()
    print("✅ Tournée terminée.")

# Test immédiat
run_all()

# Planification : Toutes les 4h
schedule.every(4).hours.do(run_all)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
