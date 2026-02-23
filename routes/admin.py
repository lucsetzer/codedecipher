from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/users")
async def admin_users(request: Request):
    # Simple auth check (optional)
    SECRET = os.getenv("ADMIN_SECRET", "change-this-in-production")
    
    conn = sqlite3.connect('/root/codedecipher/bank.db')
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT email, tokens, last_token_reset FROM users ORDER BY last_token_reset DESC")
    users = cursor.fetchall()
    
    # Get waitlist
    cursor.execute("SELECT email, signed_up FROM waitlist ORDER BY signed_up DESC")
    waitlist = cursor.fetchall()
    
    # Get pro waitlist
    cursor.execute("SELECT email, signed_up FROM pro_waitlist ORDER BY signed_up DESC")
    pro_waitlist = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": users,
        "waitlist": waitlist,
        "pro_waitlist": pro_waitlist
    })
