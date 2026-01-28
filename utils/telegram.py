"""
Telegram notification utility.
Shared helper for sending messages via Telegram Bot API.
"""

import os
import requests


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """
    Send a message via Telegram Bot API.
    
    Args:
        text: Message text to send
        parse_mode: Message format - "HTML" or "Markdown"
    
    Returns:
        True if message sent successfully, False otherwise
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print(f"Message sent successfully to chat {chat_id}")
        return True
    except requests.RequestException as e:
        print(f"Failed to send Telegram message: {e}")
        return False
