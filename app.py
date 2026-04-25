import requests
import time
import schedule

# ==== CONFIG ====
SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL"
ALERT_API_URL = "https://api.weather.gov/alerts/active"

# Keywords to filter
KEYWORDS = ["Tornado Warning", "Flash Flood Warning"]

# Avoid duplicates
sent_alerts = set()


def send_to_slack(message):
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print("Slack error:", e)


def fetch_alerts():
    try:
        response = requests.get(
            ALERT_API_URL,
            headers={"User-Agent": "weather-alert-app"}
        )
        data = response.json()

        for feature in data.get("features", []):
            props = feature.get("properties", {})
            event = props.get("event", "")
            headline = props.get("headline", "")
            area = props.get("areaDesc", "")
            description = props.get("description", "")
            alert_id = props.get("id", headline)

            if event in KEYWORDS and alert_id not in sent_alerts:
                message = f"""
🚨 {event}
📍 {area}

{headline}

{description[:300]}...
                """

                send_to_slack(message)
                sent_alerts.add(alert_id)

    except Exception as e:
        print("Fetch error:", e)


def job():
    print("Checking alerts...")
    fetch_alerts()


schedule.every(5).minutes.do(job)

if __name__ == "__main__":
    print("Weather alert app running...")
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)
