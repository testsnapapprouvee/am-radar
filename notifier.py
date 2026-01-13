import requests, os

def send(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={os.getenv('PHONE')}&apikey={os.getenv('WHATSAPP_KEY')}&text={msg}"
    requests.get(url)
