# ==========================================
# Code Generator Bot
# AI Generator (v1.2 - Improved parsing)
# ==========================================

import json
import re


# ==========================================
# PROJECT SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are a professional software engineer and code generator.

Your job is to convert a user's project idea into a complete,
well-structured software project.

IMPORTANT RULES:

1. Understand the user's idea before generating code.
2. Generate production-quality code.
3. Keep the project structure organized.
4. Never put multiple source files into one file.
5. Return every generated file separately.
6. Use the requested programming language.
7. If the project is a website, consider:
   - HTML
   - CSS
   - JavaScript
   - responsive design
   - accessibility
   - animations when appropriate
8. If the project is a Telegram bot, consider:
   - main bot file
   - configuration
   - requirements.txt
   - database when needed
   - clear project structure
9. If images are provided, reference their filenames exactly.
10. Do not invent image filenames.
11. Do not include explanations inside source files unless requested.
12. Return valid JSON only.
"""


# ==========================================
# BUILD PROMPT
# ==========================================

def build_prompt(project_type, idea, images=None, extra_requirements=None):

    if images is None:
        images = []

    if extra_requirements is None:
        extra_requirements = []

    if project_type == "website":
        project_description = """
The project is a website.

Generate a complete frontend project.
Use HTML, CSS and JavaScript unless the user
specifically requests another technology.

You MUST also include:
- README.md with setup instructions
- favicon reference
- assets folder usage when needed
"""
    elif project_type == "telegram_bot":
        project_description = """
The project is a Telegram bot.

Generate a complete Telegram bot project.
Use Python with pyTelegramBotAPI (telebot) unless
the user specifically requests another language/library.

You MUST also include:
- config.py (with placeholders for tokens)
- requirements.txt
- README.md with setup instructions
- database module when the bot needs storage
"""
    else:
        project_description = """
Generate the project according to the user's requirements.
"""

    if images:
        images_text = "\n".join(f"- {image}" for image in images)
    else:
        images_text = "No images were provided."

    if extra_requirements:
        requirements_text = "\n".join(
            f"- {requirement}" for requirement in extra_requirements
        )
    else:
        requirements_text = "No additional requirements."

    prompt = f"""
{SYSTEM_PROMPT}

PROJECT TYPE:
{project_type}

{project_description}

USER IDEA:
{idea}

PROVIDED IMAGES:
{images_text}

The images are saved inside the images/ folder.
Reference them with relative paths like:
images/image1.jpg

ADDITIONAL REQUIREMENTS:
{requirements_text}

RETURN FORMAT:

Return ONLY valid JSON using this structure:

{{
    "project_name": "project-name",
    "description": "short project description",
    "files": [
        {{
            "path": "index.html",
            "content": "complete file content"
        }},
        {{
            "path": "style.css",
            "content": "complete file content"
        }}
    ]
}}

IMPORTANT:

- The "files" array must contain complete files.
- Each file must have a unique path.
- Use relative paths only.
- Never use absolute paths.
- Never use markdown code fences.
- Never return JSON wrapped inside markdown.
- Do not omit required files.
- Keep the total size reasonable.
"""

    return prompt


# ==========================================
# CLEAN AI TEXT
# ==========================================

def clean_json_text(response):

    text = response.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Also handle ```json ... ``` anywhere
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        text = fence_match.group(1).strip()

    # Extract JSON object if wrapped in extra text
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]

    return text


# ==========================================
# PARSE AI RESPONSE
# ==========================================

def parse_response(response):

    try:
        cleaned = clean_json_text(response)
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "AI response is not valid JSON.",
        }

    if not isinstance(data, dict):
        return {
            "success": False,
            "error": "Invalid AI response.",
        }

    if "files" not in data:
        return {
            "success": False,
            "error": "AI response does not contain files.",
        }

    if not isinstance(data["files"], list):
        return {
            "success": False,
            "error": "Files must be a list.",
        }

    valid_files = []

    for file in data["files"]:
        if not isinstance(file, dict):
            continue

        path = file.get("path")
        content = file.get("content")

        if not path or content is None:
            continue

        valid_files.append({
            "path": path,
            "content": content,
        })

    if not valid_files:
        return {
            "success": False,
            "error": "No valid files were generated.",
        }

    return {
        "success": True,
        "project_name": data.get("project_name", "generated-project"),
        "description": data.get("description", ""),
        "files": valid_files,
    }
