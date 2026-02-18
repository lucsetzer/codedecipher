from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/privacy")
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

@router.get("/terms")
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})

@router.get("/refunds")
async def refunds(request: Request):
    return templates.TemplateResponse("refunds.html", {"request": request})

@router.get("/security")
async def security(request: Request):
    return templates.TemplateResponse("security.html", {"request": request})