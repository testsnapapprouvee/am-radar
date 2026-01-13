import requests

def fetch(slug):
    url = f"https://www.welcometothejungle.com/api/v1/companies/{slug}/jobs"
    r = requests.get(url).json()
    
    jobs = []
    for job in r["jobs"]:
        jobs.append({
            "id": job["id"],
            "title": job["name"],
            "location": job["office"]["city"],
            "url": job["urls"]["web"],
            "description": job["description"]
        })
    return jobs
