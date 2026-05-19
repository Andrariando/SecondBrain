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
    payload = await request.json()

    print("\n--- Incoming Webhook Payload ---")
    print(payload)
    print("--------------------------------\n")

    try:
        # Extract message and phone number from Meta's payload structure
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            if message.get("type") == "text":
                phone_number = message.get("from")
                message_text = message.get("text", {}).get("body")
                
                # Pass to LangGraph in background to quickly return 200 OK to Meta
                background_tasks.add_task(process_whatsapp_message, phone_number, message_text)
                
    except Exception as e:
        print(f"Error parsing message payload: {e}")

    return {"status": "received"}
