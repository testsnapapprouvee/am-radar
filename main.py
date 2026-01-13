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

# LISTE ATS (Inclus SuccessFactors pour Pictet, Tal.net pour Lazard, etc.)
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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") # Anti-detect Indeed
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
        # On vérifie si une de tes villes cibles est mentionnée
        if loc.lower() in location.lower() or loc.lower() in title.lower() or loc.lower() in description_snippet.lower():
            loc_ok = True
            break
    
    # Pour la Suisse, on est plus permissif si Indeed CH renvoie "Zürich" ou "Genève"
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

# --- MODULE 1 : INDEED SUISSE (NOUVEAU) ---
def scrape_indeed_ch():
    print("running: Indeed Suisse (CH)...")
    driver = get_driver()
    try:
        # URL ciblée : Suisse + Asset Mgmt + Internship
        url = "https://ch.indeed.com/jobs?q=Asset+Management&l=Switzerland&sc=0kf%3Ajt%28internship%29%3B"
        driver.get(url)
        time.sleep(random.uniform(5, 8)) # Indeed demande de la patience
        
        # Sélecteurs Indeed 2024
        cards = driver.find_elements(By.CLASS_NAME, "resultContent")
        
        print(f"Indeed CH: {len(cards)} offres trouvées")

        for card in cards:
            try:
                # Titre
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                title = title_elem.text
                
                # Boite
                try: company = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                except: company = "Indeed Company"
                
                # Lieu
                try: loc = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text
                except: loc = "Suisse"

                # Lien (remonter au parent <a>)
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
                company = card.
