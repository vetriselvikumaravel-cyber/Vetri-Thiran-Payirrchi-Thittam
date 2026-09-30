import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class PromptRequest(BaseModel):
    prompt: str
    character: str = ""
    setting: str = ""
    tone: str = ""
    style: str = ""


def _run_pipeline(prompt: str, character: str, setting: str, tone: str, style: str):
    outline = generate_outline(prompt, character, setting, tone, style)
    story = generate_story(outline, character, tone)
    image_paths = [generate_image(p["image_prompt"]) for p in outline]
    layout = build_comic_layout(outline, image_paths, story)
    pdf_path = save_pdf(layout, title=prompt[:60])
    return layout, pdf_path


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/generate")
async def generate(
    request: Request,
    prompt: str = Form(...),
    character: str = Form(""),
    setting: str = Form(""),
    tone: str = Form(""),
    style: str = Form(""),
):
    try:
        layout, pdf_path = _run_pipeline(prompt, character, setting, tone, style)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {e}")
    return templates.TemplateResponse(
        request,
        "comic_preview.html",
        {"layout": layout, "pdf_path": pdf_path, "pdf_name": os.path.basename(pdf_path)},
    )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        layout, pdf_path = _run_pipeline(
            payload.prompt, payload.character, payload.setting, payload.tone, payload.style
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {e}")
    return {"layout": layout, "pdf_path": pdf_path}


@router.get("/download/{filename}")
async def download(filename: str):
    path = os.path.join("static", "exports", os.path.basename(filename))
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="application/pdf", filename=os.path.basename(path))


@router.get("/export-success")
async def export_success(request: Request, file: str = ""):
    return templates.TemplateResponse(request, "export_success.html", {"pdf_path": file})


@router.get("/test-image")
async def test_image(prompt: str = "a brave fox in an enchanted forest, comic book style"):
    try:
        path = generate_image(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")
    return {"prompt": prompt, "image_path": path}
