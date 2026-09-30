import os
import re
import uuid

PANELS_DIR = os.path.join("static", "panels")
SD_MODEL = os.getenv("SD_MODEL", "stable-diffusion-v1-5/stable-diffusion-v1-5")

_pipe = None


def _get_pipe():
    """Load Stable Diffusion once (lazy) and reuse it."""
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import StableDiffusionPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        _pipe = StableDiffusionPipeline.from_pretrained(SD_MODEL, torch_dtype=dtype)
        _pipe = _pipe.to(device)
    return _pipe


def _safe_name(prompt: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", prompt).strip("_").lower()[:40]
    return f"{slug or 'panel'}_{uuid.uuid4().hex[:6]}.png"


def generate_image(prompt: str) -> str:
    """Generate a comic-style image, save it in static/panels, return its path."""
    os.makedirs(PANELS_DIR, exist_ok=True)
    pipe = _get_pipe()
    image = pipe(prompt, num_inference_steps=25, guidance_scale=7.5).images[0]
    path = os.path.join(PANELS_DIR, _safe_name(prompt))
    image.save(path)
    return path.replace("\\", "/")
