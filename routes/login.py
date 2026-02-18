from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from shared.auth import create_magic_link, store_magic_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def login_form(request: Request):
    """Show login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": request.query_params.get("message", "")
    })

@router.post("/login")
async def login_submit(request: Request, email: str = Form(...)):
    """Send magic link"""
    # Generate magic link
    token = create_magic_link(email)
    print(f"🔑 Token created: {token}")
    store_magic_token(email, token)

    success = store_magic_token(email, token)
    print(f"💾 Token stored: {success}")
    
    print(f"📤 Rendering check_email.html with email: {email}")
    
    # In development, show the link
    magic_link = f"http://localhost:8001/auth?token={token}"
    print(f"🔗 Magic link: {magic_link}")
    
    # In production, you'd send this via email
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "message": f"Check your email! (Dev link: {magic_link})"
    })