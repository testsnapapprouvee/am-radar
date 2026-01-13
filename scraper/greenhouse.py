import requests

def fetch(board):
    url = f"https://boards.greenhouse.io/{board}?gh_src=api"
    data = requests.get(url).text

    # Greenhouse expose JSON inside HTML → simple regex
    import re, json
    m = re.search(r'window\.__INITIAL_STATE__ = (.*?);', data)
    state = json.loads(m.group(1))

    jobs = []
    for job in state["jobs"]:
        jobs.append({
            "id": job["id"],
            "title": job["title"],
            "location": job["location"],
            "url": job["absolute_url"],
            "description": job["content"]
        })
    return jobs
