import json
import os
import re

import google.generativeai as genai

FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "models/gemini-1.5-flash")


def _clean_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def generate_outline(prompt: str, character: str = "", setting: str = "",
                     tone: str = "", style: str = "") -> list[dict]:
    """Use Gemini Flash to create a structured 5-panel comic outline.

    Returns a list of dicts: {panel, title, scene, image_prompt}
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(FLASH_MODEL)

    instruction = f"""
You are a comic book planner. Create a 5-panel comic outline.

Story idea: {prompt}
Main character: {character or "a hero"}
Setting: {setting or "any"}
Tone: {tone or "adventurous"}
Art style: {style or "comic book"}

Return ONLY a JSON array of exactly 5 objects. No markdown, no extra text.
Each object must have these keys:
  "panel": panel number (1-5),
  "title": short panel title,
  "scene": one or two sentence scene description,
  "image_prompt": a detailed prompt for an image generator, mentioning the
                  character, setting and the '{style or "comic book"}' art style.
"""
    response = model.generate_content(instruction)
    data = json.loads(_clean_json(response.text))

    outline = []
    for i, item in enumerate(data[:5], start=1):
        outline.append({
            "panel": int(item.get("panel", i)),
            "title": item.get("title", f"Panel {i}"),
            "scene": item.get("scene", ""),
            "image_prompt": item.get("image_prompt", item.get("scene", "")),
        })
    return outline
