from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import asyncpg
import os
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/waitlist")
async def waitlist_signup(request: Request, email: str = Form(...)):
    """Store email for launch notification"""
    
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    # Create table if not exists
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS waitlist (
            email TEXT PRIMARY KEY,
            signed_up TIMESTAMP
        )
    ''')
    
    # Store email
    try:
        await conn.execute(
            "INSERT INTO waitlist (email, signed_up) VALUES ($1, $2)",
            email, datetime.now()
        )
        message = "Thanks! We'll notify you at launch."
    except:
        message = "You're already on the list!"
    
    await conn.close()
    
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email,
        "message": message
    })

@router.post("/pro-waitlist")
async def pro_waitlist_signup(request: Request, email: str = Form(...)):
    """Store email for Pro plan notification"""
    
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    # Create Pro waitlist table if not exists
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS pro_waitlist (
            email TEXT PRIMARY KEY,
            signed_up TIMESTAMP
        )
    ''')
    
    try:
        await conn.execute(
            "INSERT INTO pro_waitlist (email, signed_up) VALUES ($1, $2)",
            email, datetime.now()
        )
        message = "Thanks! We'll notify you when Pro billing is ready."
    except:
        message = "You're already on the Pro waitlist!"
    
    await conn.close()
    
    return templates.TemplateResponse("waitlist_thanks.html", {
        "request": request,
        "email": email
    })