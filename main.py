import requests
from bs4 import BeautifulSoup

url = "https://www.efinancialcareers.com/jobs-Asset_Management.s002"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

jobs = soup.find_all("article")

print("ASSET MANAGEMENT JOBS FOUND:\n")

for job in jobs[:10]:
    print("-", job.text.strip())
