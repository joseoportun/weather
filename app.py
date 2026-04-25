import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

URL = "https://api.weather.gov/alerts/active"

KEYWORDS = ["Tornado Warning", "Flash Flood Warning"]


def send_to_slack(message):
    try:
        requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
    except Exception as e:
        print("Slack error:", e)


def fetch_alerts():
    headers = {"User-Agent": "weather-bot"}
    res = requests.get(URL, headers=headers, timeout=10)
    data = res.json()

    alerts_found = 0

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        event = props.get("event", "")
        area = props.get("areaDesc", "")
        headline = props.get("headline", "")
        severity = props.get("severity", "")

        if event in KEYWORDS:
            alerts_found += 1

            message = f"""
🚨 {event}
Severity: {severity}
📍 {area}

{headline}
            """

            send_to_slack(message)

    print(f"Alerts sent: {alerts_found}")


if __name__ == "__main__":
    fetch_alerts()
