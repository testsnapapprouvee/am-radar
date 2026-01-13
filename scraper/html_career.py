import requests
from bs4 import BeautifulSoup
import hashlib

def fetch(url):
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")

    jobs = []

    # Heuristique : on cherche tous les liens qui ressemblent à des offres
    for a in soup.find_all("a"):
        text = a.get_text(" ", strip=True).lower()
        href = a.get("href")

        if not href:
            continue

        keywords = ["career", "job", "position", "opening", "vacancy", "intern", "stage"]
        if any(k in text for k in keywords) or any(k in href.lower() for k in keywords):
            full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")

            # On ouvre la page de l'offre
            try:
                jr = requests.get(full_url, timeout=10)
                jsoup = BeautifulSoup(jr.text, "lxml")
                desc = jsoup.get_text(" ", strip=True)

                job_id = hashlib.md5(full_url.encode()).hexdigest()

                jobs.append({
                    "id": job_id,
                    "title": a.get_text(" ", strip=True),
                    "location": "",
                    "url": full_url,
                    "description": desc
                })
            except:
                pass

    return jobs
