from flask import Flask, request, jsonify
import os
import base64
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Google Sheets authentication
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds_json = os.environ.get("GOOGLE_CREDENTIALS_B64")

if creds_json:
    decoded = base64.b64decode(creds_json)
    creds_dict = json.loads(decoded)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Miss Odd Assistant Data")
else:
    raise Exception("Missing GOOGLE_CREDENTIALS_B64 environment variable")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = data.get("event_type")

    if event_type == "product_update":
        ws = sheet.worksheet("Products")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("product_id", ""),
            data.get("title", ""),
            data.get("vendor", ""),
            data.get("price", ""),
            data.get("status", ""),
            data.get("summary", "")
        ]
        ws.append_row(row)

    elif event_type in ["order", "order_updated", "order_cancelled", "order_fulfilled"]:
        ws = sheet.worksheet("Shopify")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("order_id", ""),
            data.get("email", ""),
            data.get("total", ""),
            data.get("line_items", ""),
            data.get("summary", ""),
            data.get("gpt_summary", "")
        ]
        ws.append_row(row)

    elif event_type == "customer_updated":
        ws = sheet.worksheet("Customers")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("customer_id", ""),
            data.get("email", ""),
            data.get("total_spent", ""),
            data.get("orders_count", ""),
            data.get("tags", ""),
            data.get("gpt_summary", "")
        ]
        ws.append_row(row)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
