import base64
from typing import Optional, Tuple

import requests


DEFAULT_MODEL = "gemini-2.0-flash-exp-image-generation"

IMAGE_MODELS = [
    "gemini-2.0-flash-exp-image-generation",
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "nano-banana",
    "nano-banana-pro-preview",
    "imagen-4.0-generate-preview-06-06",
    "imagen-4.0-ultra-generate-preview-06-06",
    "imagen-4.0-generate-001",
    "imagen-4.0-ultra-generate-001",
    "imagen-4.0-fast-generate-001",
]


class GeminiError(Exception):
    pass


def _extract_image_bytes(response_json: dict) -> Tuple[Optional[bytes], Optional[str]]:
    candidates = response_json.get("candidates", [])
    for cand in candidates:
        content = cand.get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            inline = part.get("inlineData")
            if inline and inline.get("data"):
                data_b64 = inline.get("data")
                mime_type = inline.get("mimeType")
                return base64.b64decode(data_b64), mime_type
    return None, None


def normalize_model_name(model: str) -> str:
    if model.startswith("models/"):
        return model
    return f"models/{model}"


def generate_image_bytes(
    prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> Tuple[bytes, Optional[str]]:
    if not api_key:
        raise GeminiError("Missing API key.")
    if not model:
        model = DEFAULT_MODEL
    model_path = normalize_model_name(model)

    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=90)
    except requests.RequestException as exc:
        raise GeminiError(str(exc)) from exc

    if response.status_code != 200:
        raise GeminiError(f"HTTP {response.status_code}: {response.text}")

    data = response.json()
    image_bytes, mime_type = _extract_image_bytes(data)
    if not image_bytes:
        raise GeminiError("No image data returned. Check model or prompt.")

    return image_bytes, mime_type
