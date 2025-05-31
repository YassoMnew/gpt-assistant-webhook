
from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

app = Flask(__name__)

# Set up Google Sheets access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("MissOdd Assistant Data")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = data.get("event_type")

    if event_type == "order":
        ws = sheet.worksheet("Shopify")
        row = [
            datetime.datetime.now().isoformat(),
            data.get("order_id", ""),
            data.get("email", ""),
            data.get("total_price", ""),
            data.get("line_items", ""),
            data.get("summary", "")
        ]
        ws.append_row(row)

    elif event_type == "product_update":
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

    elif event_type == "customer_update":
        ws = sheet.worksheet("Customers")
        row = [
            datetime.datetime.now().isoformat(),
            event_type,
            data.get("customer_id", ""),
            data.get("email", ""),
            data.get("total_spent", ""),
            data.get("orders_count", ""),
            data.get("tags", ""),
            data.get("summary", "")
        ]
        ws.append_row(row)

    return jsonify({"status": "ok"}), 200
