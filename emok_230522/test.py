import requests
import json

# webhook_url = (
#     "https://hooks.slack.com/services/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"
# )
payload = {"text": "Hello, World!"}
headers = {"Content-type": "application/json"}

response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
if response.status_code == 200:
    print("Message sent successfully")
else:
    print("Failed to send message. Error:", response.status_code)
