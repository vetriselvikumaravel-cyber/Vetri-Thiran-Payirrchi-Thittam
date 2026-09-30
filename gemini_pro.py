import os

import google.generativeai as genai

PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "models/gemini-1.5-pro")


def generate_story(outline: list[dict], character: str = "", tone: str = "") -> str:
    """Use Gemini Pro to expand the outline into narration + dialogue.

    Output format (one block per panel):
        Panel 1:
        Narration: ...
        Dialogue: ...
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(PRO_MODEL)

    outline_text = "\n".join(
        f"Panel {p['panel']} - {p['title']}: {p['scene']}" for p in outline
    )
    instruction = f"""
You are a comic book writer. Using the outline below, write the full story.
Main character: {character or "the hero"}
Tone: {tone or "adventurous"}

For EACH panel write exactly in this format:
Panel <number>:
Narration: <1-2 sentences of narration>
Dialogue: <character dialogue lines>

Outline:
{outline_text}

Return only the 5 panel blocks, no extra commentary.
"""
    response = model.generate_content(instruction)
    return response.text.strip()
