import requests

def fetch(company, tenant):
    url = f"https://{company}.wd1.myworkdayjobs.com/wday/cxs/{company}/{tenant}/jobs"
    payload = {"appliedFacets": {}, "limit": 50}

    r = requests.post(url, json=payload).json()

    jobs = []
    for j in r["jobPostings"]:
        jobs.append({
            "id": j["bulletFields"][0],
            "title": j["title"],
            "location": j["locationsText"],
            "url": f"https://{company}.wd1.myworkdayjobs.com/{tenant}{j['externalPath']}",
            "description": j["title"]
        })
    return jobs
