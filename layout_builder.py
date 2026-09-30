import re


def _split_story(story: str) -> dict[int, str]:
    """Split the story text into {panel_number: text}."""
    pattern = re.compile(r"(?im)^\W*panel\s*(\d+)\W*$|^\W*panel\s*(\d+)\s*[:\-]\W*")
    matches = list(pattern.finditer(story))
    result: dict[int, str] = {}
    for idx, m in enumerate(matches):
        num = int(m.group(1) or m.group(2))
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(story)
        result[num] = story[m.end():end].strip()
    return result


def build_comic_layout(outline: list[dict], image_paths: list[str], story: str) -> list[dict]:
    """Match each panel's image with its story text.

    Returns a list of dicts: {panel, title, scene, image_path, text}
    """
    story_map = _split_story(story)
    layout = []
    for i, panel in enumerate(outline):
        num = panel["panel"]
        layout.append({
            "panel": num,
            "title": panel["title"],
            "scene": panel["scene"],
            "image_path": image_paths[i] if i < len(image_paths) else "",
            "text": story_map.get(num, ""),
        })
    return layout
