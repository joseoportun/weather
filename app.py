import requests
import json
import os
import time

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
STATE_FILE = "state.json"

URL = "https://api.weather.gov/alerts/active"
KEYWORDS = ["Tornado Warning", "Flash Flood Warning"]

NO_ALERT_INTERVAL = 1800  # 30 minutes


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"alerts": [], "last_no_alert": 0}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def send_to_slack(msg):
    requests.post(SLACK_WEBHOOK_URL, json={"text": msg}, timeout=10)
    

def fetch_alerts():
    res = requests.get(URL, headers={"User-Agent": "weather-bot"}, timeout=10)
    data = res.json()

    state = load_state()
    seen = set(state.get("alerts", []))
    updated = set(seen)

    alerts_found = 0

    for f in data.get("features", []):
        p = f.get("properties", {})

        event = p.get("event", "")
        alert_id = p.get("id", "")
        area = p.get("areaDesc", "")
        headline = p.get("headline", "")

        if True:
            alerts_found += 1

            if alert_id not in seen:
                msg = f"🚨 {event}\n📍 {area}\n{headline}"
                send_to_slack(msg)
                updated.add(alert_id)

    # 👇 Handle "no alerts" heartbeat
    now = int(time.time())
    last_no_alert = state.get("last_no_alert", 0)

    if alerts_found == 0 and (now - last_no_alert > NO_ALERT_INTERVAL):
        send_to_slack("✅ No active tornado or flash flood warnings right now.")
        state["last_no_alert"] = now

    state["alerts"] = list(updated)
    save_state(state)


if __name__ == "__main__":
    fetch_alerts()
