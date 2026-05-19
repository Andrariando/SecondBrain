import os
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse

from app.graph import app_graph
from app.whatsapp import send_whatsapp_message

router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if mode == "subscribe" and token == expected_token:
        return PlainTextResponse(challenge)

    print(f"Webhook verification failed! Meta sent: '{token}' but server expected: '{expected_token}'")
    raise HTTPException(status_code=403, detail="Verification failed")

def process_whatsapp_message(phone_number: str, message_text: str):
    from langchain_core.messages import HumanMessage
    print(f"Processing message from {phone_number}: {message_text}")
    initial_state = {"messages": [HumanMessage(content=message_text)], "phone_number": phone_number}
    result = app_graph.invoke(initial_state)
    
    reply_text = result.get("reply_message")
    if reply_text:
        send_whatsapp_message(phone_number, reply_text)

@router.post("/whatsapp")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    from app.whatsapp import download_whatsapp_media
    from app.openai_client import transcribe_audio, analyze_image
    
    payload = await request.json()

    print("\n--- Incoming Webhook Payload ---")
    print(payload)
    print("--------------------------------\n")

    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            phone_number = message.get("from")
            msg_type = message.get("type")
            
            message_text = None
            
            if msg_type == "text":
                message_text = message.get("text", {}).get("body")
                
            elif msg_type == "audio":
                audio_id = message.get("audio", {}).get("id")
                if audio_id:
                    print(f"Downloading audio {audio_id}...")
                    audio_bytes = download_whatsapp_media(audio_id)
                    print("Transcribing audio...")
                    message_text = transcribe_audio(audio_bytes)
                    message_text = f"[Transcribed Voice Note]: {message_text}"
                    
            elif msg_type == "image":
                image_info = message.get("image", {})
                image_id = image_info.get("id")
                caption = image_info.get("caption", "")
                if image_id:
                    print(f"Downloading image {image_id}...")
                    image_bytes = download_whatsapp_media(image_id)
                    print("Analyzing image...")
                    analysis = analyze_image(image_bytes, caption)
                    message_text = f"[Image Upload Analysis]: {analysis}"

            if message_text:
                background_tasks.add_task(process_whatsapp_message, phone_number, message_text)
                
    except Exception as e:
        print(f"Error parsing message payload: {e}")

    return {"status": "received"}
