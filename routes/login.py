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
    
    # Store in database
    await store_magic_token(email, token)
    print(f"💾 Token stored")
    
    # ACTUALLY SEND THE EMAIL (this is the important part!)
    from shared.auth import send_magic_link
    await send_magic_link(email, token)
    
    # Show the "check your email" page
    return templates.TemplateResponse("check_email.html", {
        "request": request,
        "email": email
    })
