from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/logout")
async def logout(request: Request):
    """Log out user"""
    request.session.clear()
    return RedirectResponse("/login", status_code=303)