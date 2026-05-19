from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

# Explicitly find the .env file in the parent directory of 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path=env_path, override=True)

from app.routers.whatsapp_router import router as whatsapp_router
from app.routers.health_router import router as health_router
from app.routers.api_router import router as api_router
from app.routers.upload_router import router as upload_router

app = FastAPI(title="Second Brain Wiki")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(parent_dir, "static")), name="static")

# Mount uploads directory so frontend can access PDFs
uploads_dir = os.path.join(parent_dir, "storage", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

templates = Jinja2Templates(directory=os.path.join(parent_dir, "templates"))

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

app.include_router(health_router)
app.include_router(whatsapp_router, prefix="/webhook")
app.include_router(api_router, prefix="/api")
app.include_router(upload_router, prefix="/api/upload")
