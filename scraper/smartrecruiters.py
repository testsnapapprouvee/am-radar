import requests

def fetch(company):
    url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"
    data = requests.get(url).json()

    jobs = []
    for j in data["content"]:
        jobs.append({
            "id": j["id"],
            "title": j["name"],
            "location": j["location"]["city"],
            "url": j["ref"],
            "description": j["jobAd"]["sections"]["jobDescription"]["text"]
        })
    return jobs
