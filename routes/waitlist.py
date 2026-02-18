from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/waitlist")
async def waitlist_signup(request: Request, email: str = Form(...)):
    """Store email for launch notification"""
    
    # Create waitlist table if not exists
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waitlist (
            email TEXT PRIMARY KEY,
            signed_up TIMESTAMP
        )
    ''')
    
    # Store email
    try:
        cursor.execute(
            "INSERT INTO waitlist (email, signed_up) VALUES (?, ?)",
            (email, datetime.now())
        )
        conn.commit()
        message = "Thanks! We'll notify you at launch."
    except:
        message = "You're already on the list!"
    
    conn.close()
    
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email,
        "message": message
    })