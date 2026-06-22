from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///voicebot.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    time = Column(String)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String)
    issue = Column(String)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mobile = Column(String)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(String)
    bot_reply = Column(String)


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String)
    phone_number = Column(String)
    agent_id = Column(String)
    lead_name = Column(String)
    lead_id = Column(String)
    company_id = Column(String)
    transfer_number = Column(String)
    status = Column(String)


Base.metadata.create_all(bind=engine)
class CallResultDB(Base):
    __tablename__ = "call_results"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String)
    status = Column(String)
    duration = Column(String)
    recording_url = Column(String)
    transcript = Column(String)
    summary = Column(String)
    transfer_status = Column(String)
Base.metadata.create_all(bind=engine)
