import base64
from typing import Optional, Tuple, List

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


def _get_api_base_url(api_key: str) -> str:
    return "https://generativelanguage.googleapis.com"


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
    reference_images: Optional[List[Tuple[bytes, Optional[str]]]] = None,
) -> Tuple[bytes, Optional[str]]:
    if not api_key:
        raise GeminiError("Missing API key.")
    if not model:
        model = DEFAULT_MODEL
    model_path = normalize_model_name(model)

    base_url = _get_api_base_url(api_key)
    url = f"{base_url}/v1beta/{model_path}:generateContent?key={api_key}"
    parts = [{"text": prompt}]
    if reference_images:
        for image_bytes, image_mime in reference_images:
            if not image_bytes:
                continue
            mime_type = image_mime or "image/png"
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            parts.append({"inline_data": {"mime_type": mime_type, "data": image_b64}})

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
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


def edit_image_bytes(
    prompt: str,
    image_bytes: bytes,
    image_mime: Optional[str],
    api_key: str,
    model: str = "gemini-3-pro-image-preview",
) -> Tuple[bytes, Optional[str]]:
    if not api_key:
        raise GeminiError("Missing API key.")
    if not model:
        model = "gemini-3-pro-image-preview"
    if not image_bytes:
        raise GeminiError("Missing source image bytes.")
    model_path = normalize_model_name(model)
    mime_type = image_mime or "image/png"
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    base_url = _get_api_base_url(api_key)
    url = f"{base_url}/v1beta/{model_path}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": image_b64}},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseModalities": ["IMAGE"],
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
    except requests.RequestException as exc:
        raise GeminiError(str(exc)) from exc

    if response.status_code != 200:
        raise GeminiError(f"HTTP {response.status_code}: {response.text}")

    data = response.json()
    edited_bytes, out_mime = _extract_image_bytes(data)
    if not edited_bytes:
        raise GeminiError("No image data returned. Check model or prompt.")

    return edited_bytes, out_mime
