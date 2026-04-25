import requests
import json
import os

SLACK_WEBHOOK_URL = os.getenv(https://hooks.slack.com/services/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)

ALERT_API_URL = "https://api.weather.gov/alerts/active"

KEYWORDS = ["Tornado Warning", "Flash Flood Warning"]

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(json.load(f))


def save_state(alert_ids):
    with open(STATE_FILE, "w") as f:
        json.dump(list(alert_ids), f)


def send_to_slack(message):
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print("Slack error:", e)


def fetch_alerts():
    headers = {"User-Agent": "slack-weather-alerts"}
    response = requests.get(ALERT_API_URL, headers=headers, timeout=10)
    data = response.json()

    sent_alerts = load_state()
    new_sent_alerts = set(sent_alerts)

    for feature in data.get("features", []):
        props = feature.get("properties", {})

        event = props.get("event", "")
        alert_id = props.get("id", "")
        area = props.get("areaDesc", "")
        headline = props.get("headline", "")
        description = props.get("description", "")
        severity = props.get("severity", "")

        if event in KEYWORDS and alert_id not in sent_alerts:
            message = f"""
🚨 *{event}*
Severity: {severity}
📍 {area}

{headline}

{description[:400]}...
            """

            send_to_slack(message)
            new_sent_alerts.add(alert_id)

    save_state(new_sent_alerts)


if __name__ == "__main__":
    fetch_alerts()
