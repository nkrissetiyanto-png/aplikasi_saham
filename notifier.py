import requests
import yaml

cfg = yaml.safe_load(open("config.yaml"))
BOT_TOKEN = cfg["telegram"]["token"]
CHAT_ID = cfg["telegram"]["chat_id"]

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)
