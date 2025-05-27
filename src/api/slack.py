import requests
import os

class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_notification(self, message):
        payload = {
            "text": message
        }
        response = requests.post(self.webhook_url, json=payload)

        if response.status_code != 200:
            raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")