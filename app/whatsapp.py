import os
import requests

def send_whatsapp_message(to_phone: str, message: str):
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Failed to send WhatsApp message. Response: {response.text}")
        raise e
        
    return response.json()
def download_whatsapp_media(media_id: str) -> bytes:
    WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
    
    # 1. Get the media URL from the ID
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
    url_req = requests.get(f"https://graph.facebook.com/v20.0/{media_id}", headers=headers)
    url_req.raise_for_status()
    
    media_url = url_req.json().get("url")
    if not media_url:
        raise ValueError("Could not retrieve media URL from Meta.")
        
    # 2. Download the actual binary media using the URL
    media_req = requests.get(media_url, headers=headers)
    media_req.raise_for_status()
    
    return media_req.content
