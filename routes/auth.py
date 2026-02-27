from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from shared.auth import verify_magic_link

router = APIRouter()

@router.get("/auth")
async def auth_callback(request: Request, token: str):
    print(f" Token: {token}")
    email = await verify_magic_link(token)
    print(f"Email  is type: {type(email)}")
    
    if not email:
        return RedirectResponse("/login?error=invalid_token", status_code=303)
    
    # Set session
    request.session["user_email"] = email
    
    # Check if there was a pending redirect
    redirect_to = request.session.pop("redirect_after_login", "/analyze")
    
    return RedirectResponse(redirect_to, status_code=303)

@router.get("/start")
async def start(request: Request, redirect: str = "/analyze"):
    """Redirect to login if needed, otherwise go straight to destination"""
    user_email = request.session.get("user_email")
    
    if not user_email:
        # Store where the user wanted to go
        request.session["redirect_after_login"] = redirect
        return RedirectResponse("/login", status_code=303)
    
    return RedirectResponse(redirect, status_code=303)
