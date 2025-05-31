from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    event_type = data.get("event_type", "unknown")
    order_id = data.get("order_id", "N/A")
    email = data.get("email", "N/A")
    total = data.get("total", "N/A")
    line_items = data.get("line_items", "N/A")

    prompt = f"""
You are a helpful assistant for an e-commerce company.

A new event has occurred:
- Type: {event_type}
- Order ID: {order_id}
- Email: {email}
- Total: {total}
- Line Items: {line_items}

Summarize this event for internal team review.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        return jsonify({"status": "ok", "summary": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    return "GPT Assistant Webhook is running!", 200

if __name__ == "__main__":
    app.run(debug=True)
