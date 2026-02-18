from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from shared.auth import get_user_tokens

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/settings")
async def settings_page(request: Request):
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    tokens = get_user_tokens(user_email)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user_email": user_email,
        "tokens": tokens,
        "balance": tokens,  # Add this
        "tokens_per_month": 5  # Add this (your monthly limit)
    })

@router.post("/settings/update-email")
async def update_email(request: Request, new_email: str = Form(...)):
    """Update user email"""
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    # TODO: Update email in database
    print(f"📧 Update email from {user_email} to {new_email}")
    
    # Update session
    request.session["user_email"] = new_email
    
    return RedirectResponse("/settings?success=email_updated", status_code=303)

@router.post("/settings/delete-account")
async def delete_account(request: Request):
    """Delete user account"""
    user_email = request.session.get("user_email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)
    
    # TODO: Delete user from database
    print(f"🗑️ Delete account for {user_email}")
    
    # Clear session
    request.session.clear()
    
    return RedirectResponse("/?message=account_deleted", status_code=303)