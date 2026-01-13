import json
from scraper import welcome, greenhouse, smartrecruiters
from scoring import score
from database import seen, save
from notifier import send

companies = json.load(open("companies.json"))

for c in companies:
    if c["type"] == "welcome":
        jobs = welcome.fetch(c["slug"])
    elif c["type"] == "greenhouse":
        jobs = greenhouse.fetch(c["url"].split("/")[-1])
    elif c["type"] == "smartrecruiters":
        jobs = smartrecruiters.fetch(c["slug"])
    elif c["type"] == "html":
        jobs = html_career.fetch(c["url"])
    else:
        continue

    for j in jobs:
        j["company"] = c["name"]
        j["score"] = score(j)

        if j["score"] >= 8 and not seen(j["id"]):
            save(j)
            send(f"🔥 {j['company']} – {j['title']} ({j['location']})\n{j['url']}")
