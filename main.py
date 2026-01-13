import time
import schedule
import os
import requests
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from companies import TARGET_COMPANIES
from keywords import BLACKLIST, GOLDLIST_JOBS, DATE_KEYWORDS, LOCATIONS

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8041098189:AAGNgMa1abXsvNGtcgW0mwdpeah-bofkvmA"
TELEGRAM_CHAT_ID = "5233378719"
HISTORY_FILE = "history_v2.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except Exception as e: print(f"❌ Erreur Telegram : {e}")

def get_driver():
    """Configuration V6"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(uas)}")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def process_job(title, company, location, link, source, description_snippet=""):
    link = link.split('&')[0]
    title = title.strip() if title else "Titre Inconnu"
    company = company.strip() if company else "Entreprise Inconnue"
    
    # Nettoyage automatique des noms
    if company == "Entreprise Inconnue" or "Boite" in company:
        for target in TARGET_COMPANIES:
            if target.lower().replace(" ", "") in link.lower() or target.lower().replace(" ", "") in title.lower():
                company = target
                break
    
    print(f"   🔎 [{source}] {title} | {company}")

    if not os.path.exists(HISTORY_FILE): open(HISTORY_FILE, "w").close()
    with open(HISTORY_FILE, "r") as f: history = f.read()
    
    if link in history:
        print("      -> 🛑 Déjà traité")
        return

    # Blacklist
    for bad_word in BLACKLIST:
        if bad_word.lower() in title.lower():
            print(f"      -> 🛑 Blacklisté: '{bad_word}'")
            return

    # Localisation
    loc_ok = False
    full_text = (location + " " + title + " " + description_snippet).lower()
    
    is_target = False
    for target in TARGET_COMPANIES:
        if target.lower() in company.lower() or target.lower() in title.lower(): 
            is_target = True; break
    
    # Si c'est une Top Company, on accepte tout (on triera à la main)
    if is_target:
        loc_ok = True 
    else:
        for loc in LOCATIONS:
            if loc.lower() in full_text: loc_ok = True; break
        if "suisse" in full_text or "zurich" in full_text or "geneva" in full_text: loc_ok = True

    if not loc_ok:
        print(f"      -> 🛑 Mauvaise loc: {location}")
        return 

    # Scoring
    score = 5
    if is_target: score += 3
    for gold in GOLDLIST_JOBS:
        if gold.lower() in title.lower(): score += 2; break
    for date in DATE_KEYWORDS:
        if date.lower() in description_snippet.lower(): score += 1; break

    if score >= 6:
        print(f"      -> 🔥 SUCCÈS ({score}/10) !")
        emoji = "🔥" if score >= 8 else "✅"
        msg = f"{emoji} *{source} ({score}/10)*\n🏢 {company}\n💼 {title}\n📍 {location}\n🔗 [Voir l'offre]({link})"
        send_telegram(msg)
        with open(HISTORY_FILE, "a") as f: f.write(link + "\n")
    else:
        print(f"      -> 📉 Note trop basse ({score}/10)")

# --- FONCTION VIP : RECHERCHE ÉLARGIE ---
def scrape_vip_companies():
    print("🚀 Lancement du SCAN VIP (Recherche Large)...")
    driver = get_driver()
    vip_list = list(TARGET_COMPANIES)
    random.shuffle(vip_list)
    batch_size = 4
    
    # C'est ici que ça se joue : On définit les mots clés métiers
    job_keywords = '"Asset Management" OR "Investment" OR "Sales" OR "Portfolio" OR "Wealth Management" OR "Private Banking" OR "Analyst" OR "Equity"'
    
    try:
        for i in range(0, len(vip_list), batch_size):
            batch = vip_list[i:i + batch_size]
            companies_query = " OR ".join([f'"{c}"' for c in batch])
            
            print(f"   🎯 Scan Groupe : {', '.join(batch)}...")
            
            # Requête : (Boites) (Métiers) (Stage) -SitesPoubelles
            search_query = f'({companies_query}) ({job_keywords}) ("Stage" OR "Internship") -site:linkedin.com -site:indeed.com -site:glassdoor.com -site:welcometothejungle.com'
            
            url = f"https://www.google.com/search?q={search_query}&hl=fr"
            driver.get(url)
            time.sleep(random.uniform(4, 7))
            
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "tout refuser" in btn.text.lower() or "reject all" in btn.text.lower():
                        btn.click()
                        break
            except: pass

            results = driver.find_elements(By.CSS_SELECTOR, "div.g")
            print(f"      -> {len(results)} résultats.")
            
            for res in results:
                try:
                    title = res.find_element(By.TAG_NAME, "h3").text
                    link = res.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    company_found = "Boite VIP"
                    for comp in batch:
                        if comp.lower() in title.lower() or comp.lower() in link.lower():
                            company_found = comp
                            break
                    
                    process_job(title, company_found, "Site Direct", link, "VIP Search")
                except: continue
            
            time.sleep(2)

    except Exception as e: print(f"Erreur VIP: {e}")
    finally: driver.quit()

# --- AUTRES SCRAPERS ---

def scrape_jobteaser():
    print("running: JobTeaser...")
    driver = get_driver()
    try:
        url = "https://www.jobteaser.com/fr/job-offers?query=Asset+Management&contract=internship"
        driver.get(url)
        time.sleep(5)
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job-offers/']")
        print(f"JobTeaser: {len(links)} liens.")
        for link_elem in links:
            try:
                link = link_elem.get_attribute("href")
                text = driver.execute_script("return arguments[0].innerText;", link_elem).split('\n')
                title = text[0] if text else "Offre JT"
                company = text[1] if len(text)>1 else "JobTeaser Partner"
                process_job(title, company, "France", link, "JobTeaser")
            except: continue
    except: pass
    finally: driver.quit()

def scrape_indeed_ch():
    print("running: Indeed CH...")
    driver = get_driver()
    try:
        url = "https://ch.indeed.com/jobs?q=Asset+Management&l=Switzerland&sc=0kf%3Ajt%28internship%29%3B"
        driver.get(url)
        time.sleep(6)
        cards = driver.find_elements(By.CLASS_NAME, "resultContent")
        print(f"Indeed: {len(cards)} liens.")
        for card in cards:
            try:
                title = driver.execute_script("return arguments[0].querySelector('h2.jobTitle').innerText;", card)
                try: company = driver.execute_script("return arguments[0].querySelector('[data-testid=\"company-name\"]').innerText;", card)
                except: company = "Indeed Company"
                try: link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                except: continue
                process_job(title, company, "Suisse", link, "Indeed CH")
            except: continue
    except: pass
    finally: driver.quit()

def run_all():
    print("🚀 Démarrage V6 (Recherche Large)...")
    scrape_vip_companies()
    time.sleep(5)
    scrape_jobteaser()
    time.sleep(5)
    scrape_indeed_ch()
    print("✅ Fin V6.")

schedule.every(4).hours.do(run_all)
run_all()

if __name__ == "__main__":
    while True: schedule.run_pending(); time.sleep(60)
