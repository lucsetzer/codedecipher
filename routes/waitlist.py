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

    # After storing in DB, send yourself an email
    send_magic_link("lucsetzer@gmail.com", f"New waitlist signup: {email}")
    
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email,
        "message": message
    })

@router.post("/pro-waitlist")
async def pro_waitlist_signup(request: Request, email: str = Form(...)):
    """Store email for Pro plan notification"""
    
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    # Create Pro waitlist table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pro_waitlist (
            email TEXT PRIMARY KEY,
            signed_up TIMESTAMP
        )
    ''')
    
    try:
        cursor.execute(
            "INSERT INTO pro_waitlist (email, signed_up) VALUES (?, ?)",
            (email, datetime.now())
        )
        conn.commit()
        message = "Thanks! We'll notify you when Pro billing is ready."
    except:
        message = "You're already on the Pro waitlist!"
    
    conn.close()
    
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email,
        "message": message
    })
