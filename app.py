from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from routes.analyzers.results import router as results_router
from routes.analyzers.github import router as github_router
from routes.analyzers.security import router as security_router
from routes.analyzers.api import router as api_router
from routes.login import router as login_router
from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.logout import router as logout_router
from routes.analyze import router as analyze_router
from routes.settings import router as settings_router
from routes.legal import router as legal_router
from routes.waitlist import router as waitlist_router
from starlette.middleware.sessions import SessionMiddleware
import secrets

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="CodeDecipher")

# Routers
app.include_router(results_router)
app.include_router(github_router)
app.include_router(security_router)
app.include_router(api_router)
app.include_router(login_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(logout_router)
app.include_router(analyze_router)
app.include_router(settings_router)
app.include_router(legal_router)
app.include_router(waitlist_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

print("🚀 Starting app.py")
print(f"🔍 Current directory: {os.getcwd()}")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", secrets.token_urlsafe(32)),
    max_age=86400,  # 24 hours
    same_site="lax",
    https_only=False  # Set to True in production with HTTPS
)

# Import ONLY the routers we actually have
from routes.analyzers.snippet import router as snippet_router
print("✅ Snippet router imported")

# Include routers
app.include_router(snippet_router)
print("✅ Snippet router imported")

@app.get("/")
async def home(request: Request):
    """Landing page"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("frontpage.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/debug-routes")
async def debug_routes():
    routes_list = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            routes_list.append(f"{route.path} [{','.join(route.methods)}]")
        else:
            routes_list.append(f"{route.path} [MOUNT]")
    return {"routes": routes_list}