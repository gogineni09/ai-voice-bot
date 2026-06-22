from anthropic import Anthropic
from dotenv import load_dotenv
import os
load_dotenv(".env")
from openai import OpenAI

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import (
    SessionLocal,
    Appointment,
    Ticket,
    Customer,
    ChatHistory,
    Call,
    CallResultDB
)
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

memory = {}
ticket_counter = 1001


@app.get("/")
def home():
    return FileResponse("templates/index.html")


class Message(BaseModel):
    message: str
class CallRequest(BaseModel):
    phone_number: str
    agent_id: str
    lead_name: str
    lead_id: str
    company_id: str
    transfer_number: str


class CallResult(BaseModel):
    call_id: str
    status: str
    duration: str
    recording_url: str
    transcript: str
    summary: str
    transfer_status: str


@app.post("/chat")
def chat(msg: Message):

    global ticket_counter

    text = msg.message.strip()
    reply = ""
    # Name Memory
    if text.lower().startswith("my name is"):
        name = text[10:].strip()
        memory["name"] = name
        reply = f"Nice to meet you, {name}!"

    elif "what is my name" in text.lower():

        if "name" in memory:
            reply = f"Your name is {memory['name']}."
        else:
            reply = "I don't know your name yet."

    # Appointment
    elif text.lower() == "appointment":
        memory["appointment_step"] = "date"
        reply = "Please enter appointment date."

    elif memory.get("appointment_step") == "date":
        memory["appointment_date"] = text
        memory["appointment_step"] = "time"
        reply = "Please enter appointment time."

    elif memory.get("appointment_step") == "time":

        date = memory["appointment_date"]
        time = text

        db = SessionLocal()

        appointment = Appointment(
            date=date,
            time=time
        )

        db.add(appointment)
        db.commit()
        db.close()

        memory.pop("appointment_step", None)
        memory.pop("appointment_date", None)

        reply = f"Appointment booked for {date} at {time}"

    # Support Ticket
    elif text.lower() == "support":
        memory["support_step"] = "issue"
        reply = "Please describe your issue."

    elif memory.get("support_step") == "issue":

        issue = text

        ticket_id = f"TKT{ticket_counter}"
        ticket_counter += 1

        db = SessionLocal()

        ticket = Ticket(
            ticket_id=ticket_id,
            issue=issue
        )

        db.add(ticket)
        db.commit()
        db.close()

        memory.pop("support_step", None)

        reply = f"Ticket created successfully. ID: {ticket_id}"

    # Customer Verification
    elif text.lower() == "verify customer":
        memory["customer_step"] = "name"
        reply = "Please enter your name."

    elif memory.get("customer_step") == "name":
        memory["customer_name"] = text
        memory["customer_step"] = "mobile"
        reply = "Please enter your mobile number."

    elif memory.get("customer_step") == "mobile":

        name = memory["customer_name"]
        mobile = text

        db = SessionLocal()

        customer = Customer(
            name=name,
            mobile=mobile
        )

        db.add(customer)
        db.commit()
        db.close()

        memory.pop("customer_step", None)
        memory.pop("customer_name", None)

        reply = f"Customer verified successfully. Name: {name}"
    elif "hello" in text.lower():
        reply = "Hello! How can I help you today?"

    else:
        try:
            response = openrouter_client.chat.completions.create(
                model="openai/gpt-oss-20b:free",
                messages=[
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )

            reply = response.choices[0].message.content

        except Exception as e:
            reply = f"AI Error: {str(e)}"

    # Save Chat History
    db = SessionLocal()

    chat = ChatHistory(
        user_message=text,
        bot_reply=reply
    )

    db.add(chat)
    db.commit()
    db.close()

    return {"reply": reply}

@app.get("/tickets")
def get_tickets():
    db = SessionLocal()
    data = db.query(Ticket).all()
    db.close()
    return data

@app.get("/history")
def get_history():
    db = SessionLocal()
    data = db.query(ChatHistory).all()
    db.close()
    return data

@app.get("/analytics")
def analytics():

    db = SessionLocal()

    appointments = db.query(Appointment).count()
    tickets = db.query(Ticket).count()
    customers = db.query(Customer).count()
    chats = db.query(ChatHistory).count()

    total_calls = db.query(Call).count()

    completed_calls = db.query(CallResultDB).filter(
        CallResultDB.status == "completed"
    ).count()

    print("TOTAL CALLS =", total_calls)
    print("COMPLETED CALLS =", completed_calls)

    db.close()

    return {
        "appointments": appointments,
        "tickets": tickets,
        "customers": customers,
        "chat_messages": chats,
        "total_calls": total_calls,
        "completed_calls": completed_calls
    }
@app.get("/test-ai")
def test_ai():

    try:
        response = openrouter_client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        )

        return {
            "response": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "error": str(e)
        }

@app.post("/make-call")
def make_call(data: CallRequest):

    db = SessionLocal()

    call_id = f"CALL{data.lead_id}"

    call = Call(
        call_id=call_id,
        phone_number=data.phone_number,
        agent_id=data.agent_id,
        lead_name=data.lead_name,
        lead_id=data.lead_id,
        company_id=data.company_id,
        transfer_number=data.transfer_number,
        status="initiated"
    )

    db.add(call)
    db.commit()
    db.close()

    return {
        "call_id": call_id,
        "status": "initiated"
    }


@app.get("/calls")
def get_calls():

    db = SessionLocal()
    data = db.query(Call).all()
    db.close()

    return data


    db.add(result)
    db.commit()
    db.close()

    return {
        "message": "Call result saved",
        "call_id": data.call_id
    }


@app.post("/webhook/call-result")
def call_result(data: CallResult):

    db = SessionLocal()

    call = db.query(Call).filter(
        Call.call_id == data.call_id
    ).first()

    if call:
        call.status = data.status

    result = CallResultDB(
        call_id=data.call_id,
        status=data.status,
        duration=data.duration,
        recording_url=data.recording_url,
        transcript=data.transcript,
        summary=data.summary,
        transfer_status=data.transfer_status
    )

    db.add(result)
    db.commit()
    db.close()

    return {
        "message": "Call result saved",
        "call_id": data.call_id
    }

@app.post("/webhook/call-result")
def call_result(data: CallResult):

    db = SessionLocal()

    result = CallResultDB(
        call_id=data.call_id,
        status=data.status,
        duration=data.duration,
        recording_url=data.recording_url,
        transcript=data.transcript,
        summary=data.summary,
        transfer_status=data.transfer_status
    )

    db.add(result)
    db.commit()
    db.close()

    return {
        "message": "Call result saved",
        "call_id": data.call_id
    }
  