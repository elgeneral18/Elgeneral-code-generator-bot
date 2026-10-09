# ==========================================
# Code Generator Bot
# AI Client (v1.2 - Robust error handling)
# ==========================================

import requests

from config import GEMINI_API_KEY, GEMINI_MODEL


URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def generate(prompt):
    """Send prompt to Gemini and return structured result."""

    try:
        response = requests.post(
            URL,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY,
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 65536,
                },
            },
            timeout=180,
        )

        data = response.json()

        if response.status_code != 200:
            error_msg = data.get("error", {}).get("message", str(data))
            return {
                "success": False,
                "error": f"API Error ({response.status_code}): {error_msg}",
            }

        # Handle blocked / empty responses safely
        candidates = data.get("candidates")
        if not candidates:
            prompt_feedback = data.get("promptFeedback", {})
            block_reason = prompt_feedback.get("blockReason", "unknown")
            return {
                "success": False,
                "error": f"No candidates returned. Block reason: {block_reason}",
            }

        candidate = candidates[0]

        # Check finish reason
        finish_reason = candidate.get("finishReason", "")
        if finish_reason and finish_reason not in ("STOP", "MAX_TOKENS"):
            return {
                "success": False,
                "error": f"Generation stopped: {finish_reason}",
            }

        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            return {
                "success": False,
                "error": "Empty response from model (no parts).",
            }

        text = parts[0].get("text", "")
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text content from model.",
            }

        return {
            "success": True,
            "text": text,
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. Try again.",
        }
    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": f"Network error: {error}",
        }
    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }
