import os
import json
import urllib.request
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def call_telegram(method, payload):
    url = f"{API_URL}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message_with_button(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "بزن ببین چی میشه", "callback_data": "test_click"}]
            ]
        },
    }
    call_telegram("sendMessage", payload)


def answer_callback(callback_query_id, text):
    call_telegram(
        "answerCallbackQuery",
        {"callback_query_id": callback_query_id, "text": text, "show_alert": False},
    )


def send_plain_message(chat_id, text):
    call_telegram("sendMessage", {"chat_id": chat_id, "text": text})


@app.route("/", methods=["GET"])
def health_check():
    # Render برای بررسی زنده بودن سرویس این مسیر رو صدا می‌زنه
    return "Bot is running.", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)

    # حالت ۱: کاربر یک پیام متنی فرستاده (مثلاً /start)
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        if text == "/start":
            send_message_with_button(chat_id, "سلام! این یه بات تستیه 👇")
        else:
            send_plain_message(chat_id, "فقط /start رو امتحان کن فعلاً.")

    # حالت ۲: کاربر روی دکمه زده
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        if callback["data"] == "test_click":
            answer_callback(callback["id"], "دکمه کار کرد!")
            send_plain_message(chat_id, "دکمه کار کرد! ✅")

    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
