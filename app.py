import requests
import json
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
STATE_FILE = "state.json"

URL = "https://api.weather.gov/alerts/active"
KEYWORDS = ["Tornado Warning", "Flash Flood Warning"]


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(json.load(f))


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(list(state), f)


def send_to_slack(msg):
    requests.post(SLACK_WEBHOOK_URL, json={"text": msg}, timeout=10)


def fetch_alerts():
    res = requests.get(URL, headers={"User-Agent": "bot"}, timeout=10)
    data = res.json()

    seen = load_state()
    updated = set(seen)

    for f in data.get("features", []):
        p = f.get("properties", {})

        event = p.get("event", "")
        alert_id = p.get("id", "")
        area = p.get("areaDesc", "")
        headline = p.get("headline", "")

        if event in KEYWORDS and alert_id not in seen:
            msg = f"🚨 {event}\n📍 {area}\n{headline}"
            send_to_slack(msg)
            updated.add(alert_id)

    save_state(updated)


if __name__ == "__main__":
    fetch_alerts()
