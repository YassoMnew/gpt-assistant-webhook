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

    elif event_type in ["order", "order_fulfilled", "order_updated", "order_created", "order_cancelled"]:
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

    elif event_type == "customer":
        ws = sheet.worksheet("Customers")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("customer_id", ""),
            data.get("email", ""),
            data.get("name", ""),
            data.get("tags", ""),
            data.get("summary", ""),
        ]
        ws.append_row(row)

    return jsonify({"status": "ok"})

@app.route("/test", methods=["GET"])
def test():
    ws = sheet.worksheet("Products")
    row = [
        datetime.datetime.now().isoformat(),  # timestamp
        "test",        # event_type
        "123",         # product_id
        "Test Product",# title
        "MissOdd",     # vendor
        "100",         # price
        "active",      # status
        "testing row"  # gpt_summary
    ]
    ws.append_row(row)
    return jsonify({"status": "test row added"})

@app.route("/summary/orders", methods=["GET"])
def summarize_orders():
    ws = sheet.worksheet("Shopify")
    rows = ws.get_all_values()
    header, data = rows[0], rows[1:]
    recent = data[-10:]
    total_value = sum(float(row[4]) if row[4] else 0 for row in recent)
    return jsonify({"summary": f"Latest {len(recent)} orders processed. Total value: {total_value}."})

@app.route("/summary/customers", methods=["GET"])
def summarize_customers():
    ws = sheet.worksheet("Customers")
    rows = ws.get_all_values()
    header, data = rows[0], rows[1:]
    count = len(data)
    tags = set(tag for row in data for tag in row[5].split(",") if tag)
    return jsonify({"summary": f"{count} customers tracked. Active segments: {', '.join(tags)}."})

@app.route("/summary/products", methods=["GET"])
def summarize_products():
    ws = sheet.worksheet("Products")
    rows = ws.get_all_values()
    header, data = rows[0], rows[1:]
    total_products = len(data)
    published = sum(1 for row in data if row[6].lower() == "published")
    return jsonify({"summary": f"{total_products} products, {published} are published."})
