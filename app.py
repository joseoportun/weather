import requests
import os
import datetime

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_test_message():
    if not SLACK_WEBHOOK_URL:
        print("❌ Missing SLACK_WEBHOOK_URL")
        return

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    message = f"""
🧪 Test Notification
Your Slack weather bot is alive.

Time: {now}

If you see this, everything is working.
    """

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=10
        )
        print("Status:", response.status_code)
    except Exception as e:
        print("Error sending message:", e)


if __name__ == "__main__":
    send_test_message()
