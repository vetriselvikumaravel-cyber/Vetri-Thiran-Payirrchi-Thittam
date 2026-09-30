import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.routes import router  # noqa: E402  (after load_dotenv)

os.makedirs("static/panels", exist_ok=True)
os.makedirs("static/exports", exist_ok=True)

app = FastAPI(title="ComicCraft - AI Comic Story Creator")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
