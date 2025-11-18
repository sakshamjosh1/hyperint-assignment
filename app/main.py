# app/main.py
import os
import asyncio
import time
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "reviewsdb")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

# retry config
DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "15"))   # how many attempts
DB_CONNECT_DELAY = float(os.getenv("DB_CONNECT_DELAY", "1.0"))   # seconds between attempts
DB_CONNECT_TIMEOUT = float(os.getenv("DB_CONNECT_TIMEOUT", "30"))  # total timeout (seconds), optional

app = FastAPI(title="Hyperint SDE Assignment Backend")

# In-memory session store: phone_number -> {"step": int, "product": str, "name": str}
sessions: Dict[str, Dict[str, Any]] = {}

db_pool: pool.SimpleConnectionPool | None = None

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50),
    user_name VARCHAR(255),
    product_name VARCHAR(255),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
"""

INSERT_REVIEW_SQL = """
INSERT INTO reviews (phone, user_name, product_name, review_text)
VALUES (%s, %s, %s, %s);
"""

SELECT_ALL_SQL = """
SELECT id, phone, user_name, product_name, review_text, created_at
FROM reviews
ORDER BY created_at DESC;
"""

def init_db_pool():
    """
    Initialize a psycopg2 SimpleConnectionPool with retries/backoff.
    This avoids fast-failing when Postgres container is still starting.
    """
    global db_pool
    if db_pool is not None:
        return

    last_exc = None
    start_time = time.time()
    for attempt in range(1, DB_CONNECT_RETRIES + 1):
        try:
            print(f"[db] Attempt {attempt} to connect to Postgres at {DB_HOST}:{DB_PORT}...")
            db_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                connect_timeout=5,
            )
            # quick test connection: get and put one
            conn = db_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    _ = cur.fetchone()
            finally:
                db_pool.putconn(conn)
            print("[db] Connected to Postgres and pool created.")
            return
        except Exception as e:
            last_exc = e
            elapsed = time.time() - start_time
            if DB_CONNECT_TIMEOUT and elapsed > DB_CONNECT_TIMEOUT:
                print(f"[db] Timeout reached after {elapsed:.1f}s while trying to connect.")
                break
            print(f"[db] Connection attempt {attempt} failed: {e!r}. Retrying in {DB_CONNECT_DELAY}s...")
            time.sleep(DB_CONNECT_DELAY)

    # if we get here, we failed to connect
    raise RuntimeError(f"Could not connect to Postgres after {DB_CONNECT_RETRIES} attempts. Last error: {last_exc!r}")

def close_db_pool():
    global db_pool
    if db_pool:
        db_pool.closeall()
        db_pool = None

def run_blocking(fn, *args, **kwargs):
    """Helper: run blocking DB call in a thread to avoid blocking event loop."""
    return asyncio.to_thread(fn, *args, **kwargs)

def create_table():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            conn.commit()
    finally:
        db_pool.putconn(conn)

def insert_review_sync(phone: str, user_name: str, product_name: str, review_text: str):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(INSERT_REVIEW_SQL, (phone, user_name, product_name, review_text))
            conn.commit()
    finally:
        db_pool.putconn(conn)

def select_all_sync():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_ALL_SQL)
            rows = cur.fetchall()
            # convert rows to dicts
            result = []
            for r in rows:
                result.append({
                    "id": r[0],
                    "phone": r[1],
                    "user_name": r[2],
                    "product_name": r[3],
                    "review_text": r[4],
                    "created_at": r[5].isoformat() if r[5] else None
                })
            return result
    finally:
        db_pool.putconn(conn)

@app.on_event("startup")
async def startup():
    # initialize db pool with retries
    init_db_pool()
    # create table in background thread
    await run_blocking(create_table)
    print("DB pool initialized and table ensured.")

@app.on_event("shutdown")
async def shutdown():
    close_db_pool()
    print("DB pool closed.")

@app.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(request: Request):
    """
    Twilio will POST form-encoded data here when a WhatsApp message arrives.
    Important fields: 'From' (the sender phone), 'Body' (message text).
    We'll respond with TwiML XML (simple <Response><Message>...).
    """
    form = await request.form()
    from_phone = form.get("From") or form.get("from") or ""
    body = form.get("Body") or form.get("body") or ""
    from_phone = str(from_phone)
    body = str(body).strip()

    if not from_phone:
        raise HTTPException(status_code=400, detail="Missing 'From' in request form data.")

    # Normalize phone key for sessions (twilio includes "whatsapp:" prefix)
    phone_key = from_phone.replace("whatsapp:", "")

    # Initialize session if new
    session = sessions.get(phone_key)
    if session is None:
        session = {"step": 0, "product": None, "name": None}
        sessions[phone_key] = session

    # Conversation flow:
    # step 0 -> ask for product name
    # step 1 -> ask for user name
    # step 2 -> ask for review text
    # step 3 -> save review and reset session

    reply = ""

    if session["step"] == 0:
        # If user typed something immediately, treat it as product; else prompt.
        if body:
            session["product"] = body
            session["step"] = 1
            reply = f"Cool — product: *{session['product']}*. What's your name?"
        else:
            reply = "Hi! What product would you like to review?"
    elif session["step"] == 1:
        if body:
            session["name"] = body
            session["step"] = 2
            reply = f"Thanks, {session['name']}! Please send your review for *{session['product']}* (a short sentence is fine)."
        else:
            reply = "Please tell me your name so I can save the review with it."
    elif session["step"] == 2:
        if body:
            review_text = body
            # save to DB in background
            await run_blocking(insert_review_sync, phone_key, session["name"], session["product"], review_text)
            reply = "✅ Thanks! Your review has been saved. Want to review another product? Reply YES or NO."
            session["step"] = 3
        else:
            reply = "Please type your review message now."
    elif session["step"] == 3:
        # expecting YES/NO to restart or end
        if body.lower() in ("yes", "y"):
            sessions[phone_key] = {"step": 0, "product": None, "name": None}
            reply = "Awesome — what product would you like to review next?"
        else:
            sessions.pop(phone_key, None)
            reply = "Thanks! If you'd like to add more reviews later, just send a message. Bye!"

    # Twilio expects XML TwiML for reply. We'll return plain XML text and correct content-type.
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>"""
    return PlainTextResponse(content=twiml, media_type="application/xml")

@app.get("/api/reviews")
async def get_reviews():
    rows = await run_blocking(select_all_sync)
    return JSONResponse(content={"reviews": rows})
