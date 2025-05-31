
from flask import Flask, request, jsonify
import os
import base64
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Set up Google Sheets access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get("GOOGLE_CREDENTIALS_B64")

if creds_json:
    decoded = base64.b64decode(creds_json)
    creds_dict = json.loads(decoded)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Miss Odd Assistant Data")
else:
    raise Exception("Missing GOOGLE_CREDENTIALS_B64 environment variable")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = data.get("event_type", "")

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
            data.get("gpt_summary", ""),
        ]
        ws.append_row(row)

    elif event_type == "order":
        ws = sheet.worksheet("Shopify")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("order_id", ""),
            data.get("email", ""),
            data.get("total", ""),
            data.get("Line Items", ""),
            data.get("Summary", ""),
            data.get("gpt_summary", ""),
        ]
        ws.append_row(row)

    elif event_type == "customer_update":
        ws = sheet.worksheet("Customers")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("customer_id", ""),
            data.get("email", ""),
            data.get("first_name", ""),
            data.get("last_name", ""),
            data.get("summary", ""),
            data.get("gpt_summary", ""),
        ]
        ws.append_row(row)

    return jsonify({"status": "ok"})
