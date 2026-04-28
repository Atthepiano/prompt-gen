"""OpenAI / LiteLLM Image Generation Service.

Handles two distinct parameter families:
  - gpt-image-*  : modern models (gpt-image-1, gpt-image-1-mini, gpt-image-1.5, gpt-image-2)
                   use `output_format`, NOT `response_format`
  - dall-e-*     : legacy models (dall-e-2, dall-e-3)
                   use `response_format`, do NOT support `quality`

Both are routed through the standard /v1/images/generations endpoint
(or a compatible LiteLLM relay at a custom base_url).
"""
from __future__ import annotations

import base64
import io
from typing import Optional, Tuple, List

import requests

# ---------------------------------------------------------------------------
# Model catalogue (updated April 2026)
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "gpt-image-2"

IMAGE_MODELS = [
    "gpt-image-2",          # Apr 2026 - latest, reasoning-enhanced
    "gpt-image-1.5",        # Dec 2025 - 4x faster than gpt-image-1
    "gpt-image-1",          # Apr 2025 - first natively multimodal
    "gpt-image-1-mini",     # Oct 2025 - 80% cheaper than gpt-image-1
]

# Legacy DALL-E models (deprecating May 12 2026, kept for backward compat)
LEGACY_MODELS = [
    "dall-e-3",
    "dall-e-2",
]

ALL_MODELS = IMAGE_MODELS + LEGACY_MODELS

DEFAULT_BASE_URL = "https://api.openai.com/v1"

# Sizes supported by gpt-image family
SIZES_GPT_IMAGE = ["1024x1024", "1536x1024", "1024x1536", "auto"]
# Sizes supported by DALL-E family
SIZES_DALLE3 = ["1024x1024", "1792x1024", "1024x1792"]
SIZES_DALLE2 = ["256x256", "512x512", "1024x1024"]

# Quality options (gpt-image family only; DALL-E 3 has hd/standard, DALL-E 2 has none)
QUALITY_OPTIONS = ["auto", "high", "medium", "low"]


class OpenAIError(Exception):
    pass


def _is_gpt_image(model: str) -> bool:
    return model.startswith("gpt-image")


# ---------------------------------------------------------------------------
# Artist-name sanitization (copyright protection) -- delegated to separate module
# ---------------------------------------------------------------------------
from core.prompt_sanitizer import sanitize_for_openai  # noqa: E402

# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def _raise_api_error(resp: requests.Response) -> None:
    """Parse an error response and raise OpenAIError with a human-readable message."""
    status = resp.status_code

    try:
        body = resp.json()
    except Exception:
        raise OpenAIError(f"HTTP {status}: {resp.text[:400]}")

    err_obj = body.get("error") or {}
    if isinstance(err_obj, str):
        err_obj = {}

    code = (err_obj.get("code") or err_obj.get("type") or
            body.get("code") or body.get("type") or "")
    message = (err_obj.get("message") or
               body.get("message") or
               resp.text[:400])

    code_lower = str(code).lower()
    msg_lower = str(message).lower()

    # Content moderation / policy violation
    if any(k in code_lower for k in ("moderation", "content_policy", "safety")):
        raise OpenAIError(
            "[Content Filter] HTTP {}: Prompt rejected by content safety system.\n"
            "Tip: gpt-image-2 may reject minors, body-part terms, military/weapon language.\n"
            "Detail: {}".format(status, message)
        )

    if "moderation" in msg_lower or "content policy" in msg_lower or "safety system" in msg_lower:
        raise OpenAIError(
            "[Content Filter] HTTP {}: Prompt rejected by content safety system.\n"
            "Tip: gpt-image-2 may reject minors, body-part terms, military/weapon language.\n"
            "Detail: {}".format(status, message)
        )

    # Authentication
    if status == 401 or "invalid_api_key" in code_lower or "unauthorized" in msg_lower:
        raise OpenAIError(
            "[Auth Error] HTTP {}: Invalid or missing API key.\n"
            "Check your OpenAI API key in Settings.\n"
            "Detail: {}".format(status, message)
        )

    # Model not found / not supported
    if ("model_not_found" in code_lower or "invalid_model" in code_lower
            or "no such model" in msg_lower or "invalid model name" in msg_lower
            or "model name" in msg_lower):
        raise OpenAIError(
            "[Model Error] HTTP {}: Model not supported on this relay.\n"
            "Try a different model, or check your relay's /v1/models list.\n"
            "Detail: {}".format(status, message)
        )

    # Rate limit
    if status == 429 or "rate_limit" in code_lower:
        raise OpenAIError(
            "[Rate Limit] HTTP {}: Too many requests. Wait a moment and retry.\n"
            "Detail: {}".format(status, message)
        )

    # Quota / billing
    if "quota" in msg_lower or "billing" in msg_lower or "insufficient_quota" in code_lower:
        raise OpenAIError(
            "[Quota] HTTP {}: API quota exceeded or billing issue.\n"
            "Detail: {}".format(status, message)
        )

    # Generic fallback
    parts = []
    if code:
        parts.append("code={}".format(code))
    parts.append(str(message))
    raise OpenAIError("HTTP {}: {}".format(status, " | ".join(parts)))


# ---------------------------------------------------------------------------
# Response decoder
# ---------------------------------------------------------------------------

def _decode_response_image(response_json: dict) -> Tuple[bytes, str]:
    """Extract the first image from an OpenAI/LiteLLM images response.

    Handles three possible response shapes:
      - data[0].b64_json   (DALL-E or gpt-image with output_format=b64)
      - data[0].url        (URL to download)
      - data[0].b64        (some LiteLLM relay variants)
    """
    data = response_json.get("data", [])
    if not data:
        raise OpenAIError("No image data in response.")

    item = data[0]

    # b64_json (DALL-E style)
    b64 = item.get("b64_json") or item.get("b64")
    if b64:
        return base64.b64decode(b64), "image/png"

    # url -- download it
    url = item.get("url")
    if url:
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            content_type = r.headers.get("Content-Type", "image/png").split(";")[0]
            return r.content, content_type
        except requests.RequestException as exc:
            raise OpenAIError("Failed to download image from URL: {}".format(exc)) from exc

    raise OpenAIError("Unrecognised response shape: {}".format(list(item.keys())))


# ---------------------------------------------------------------------------
# Parameter builders -- separate for gpt-image vs DALL-E
# ---------------------------------------------------------------------------

def _build_gpt_image_payload(model, prompt, size, quality):
    """Minimal payload for gpt-image-* models.

    Key differences from DALL-E:
      - NO response_format (not supported; causes 400 on some relays)
      - NO n (omit; defaults to 1; some relays reject explicit n)
      - quality: "auto"|"low"|"medium"|"high"  (NOT hd/standard)
      - size: 1024x1024 | 1536x1024 | 1024x1536  (not the DALL-E sizes)
    """
    payload = {"model": model, "prompt": prompt}
    if size and size != "auto":
        payload["size"] = size
    if quality and quality != "auto":
        payload["quality"] = quality
    return payload


def _build_dalle_payload(model, prompt, size, quality):
    """Payload for legacy dall-e-2 / dall-e-3 models.

    Key differences from gpt-image:
      - response_format: "url" (supported and recommended)
      - n: 1 explicit is fine
      - quality: "standard" | "hd"  (DALL-E 3 only)
      - size: DALL-E 3 uses 1024x1024 | 1792x1024 | 1024x1792
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "response_format": "url",
    }
    if size and size not in ("auto",):
        payload["size"] = size
    # DALL-E 3 supports quality=hd; map our "high" -> "hd", ignore others
    if model == "dall-e-3" and quality == "high":
        payload["quality"] = "hd"
    return payload


def _build_headers(api_key):
    return {
        "Authorization": "Bearer {}".format(api_key),
        "Content-Type": "application/json",
    }


def _generations_url(base_url):
    return base_url.rstrip("/") + "/images/generations"


def _edits_url(base_url):
    return base_url.rstrip("/") + "/images/edits"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_image_bytes(
    prompt,
    api_key,
    model=DEFAULT_MODEL,
    base_url=DEFAULT_BASE_URL,
    size="1024x1024",
    quality="auto",
    reference_images=None,
    n=1,
):
    """Generate an image from a text prompt.

    Automatically selects the correct request structure for gpt-image vs DALL-E.
    If reference_images are supplied, routes to /images/edits (gpt-image only).
    """
    if not api_key:
        raise OpenAIError("Missing OpenAI API key.")
    if not model:
        model = DEFAULT_MODEL

    # Strip artist names from prompt (gpt-image copyright protection)
    if _is_gpt_image(model):
        prompt = sanitize_for_openai(prompt)

    # DEBUG: write the actual prompt sent to API (remove after testing)
    try:
        import os
        _log = os.path.join(os.path.dirname(__file__), "..", "last_openai_prompt.txt")
        with open(_log, "w", encoding="utf-8") as _f:
            _f.write(prompt)
    except Exception:
        pass

    # Reference images -> edits endpoint (gpt-image only)
    if reference_images and _is_gpt_image(model):
        return _edit_with_references(
            prompt=prompt, api_key=api_key, model=model,
            base_url=base_url, size=size, quality=quality,
            reference_images=reference_images,
        )

    # Choose payload builder
    if _is_gpt_image(model):
        payload = _build_gpt_image_payload(model, prompt, size, quality)
    else:
        payload = _build_dalle_payload(model, prompt, size, quality)

    endpoint = _generations_url(base_url)
    headers = _build_headers(api_key)

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=480)
    except requests.RequestException as exc:
        raise OpenAIError(str(exc)) from exc

    if resp.status_code != 200:
        _raise_api_error(resp)

    return _decode_response_image(resp.json())


def _edit_with_references(prompt, api_key, model, base_url, size, quality, reference_images):
    """Call /images/edits with multipart form data (gpt-image models only)."""
    endpoint = _edits_url(base_url)
    headers = {"Authorization": "Bearer {}".format(api_key)}

    files = []
    primary_bytes, primary_mime = reference_images[0]
    primary_mime = primary_mime or "image/png"
    ext = "png" if "png" in primary_mime else "webp"
    files.append(("image", ("image.{}".format(ext), io.BytesIO(primary_bytes), primary_mime)))

    for idx, (img_bytes, img_mime) in enumerate(reference_images[1:], start=1):
        img_mime = img_mime or "image/png"
        ext2 = "png" if "png" in img_mime else "webp"
        files.append(("image[]", ("ref_{}.{}".format(idx, ext2), io.BytesIO(img_bytes), img_mime)))

    # Edits endpoint uses form data, not JSON -- same minimal param rules
    data = {"model": model, "prompt": prompt}
    if size and size != "auto":
        data["size"] = size
    if quality and quality != "auto":
        data["quality"] = quality

    try:
        resp = requests.post(endpoint, data=data, files=files, headers=headers, timeout=480)
    except requests.RequestException as exc:
        raise OpenAIError(str(exc)) from exc

    if resp.status_code != 200:
        _raise_api_error(resp)

    return _decode_response_image(resp.json())


def edit_image_bytes(
    prompt,
    image_bytes,
    image_mime,
    api_key,
    model=DEFAULT_MODEL,
    base_url=DEFAULT_BASE_URL,
    size="1024x1024",
    quality="auto",
):
    """Edit / inpaint an existing image using the edits endpoint."""
    if _is_gpt_image(model):
        prompt = sanitize_for_openai(prompt)
        return _edit_with_references(
            prompt=prompt, api_key=api_key, model=model,
            base_url=base_url, size=size, quality=quality,
            reference_images=[(image_bytes, image_mime)],
        )
    else:
        # DALL-E edit -- same edits endpoint but different params
        endpoint = _edits_url(base_url)
        headers = {"Authorization": "Bearer {}".format(api_key)}
        mime = image_mime or "image/png"
        ext = "png" if "png" in mime else "webp"
        files = [("image", ("image.{}".format(ext), io.BytesIO(image_bytes), mime))]
        data = {"model": model, "prompt": prompt, "n": "1", "response_format": "url"}
        try:
            resp = requests.post(endpoint, data=data, files=files, headers=headers, timeout=480)
        except requests.RequestException as exc:
            raise OpenAIError(str(exc)) from exc
        if resp.status_code != 200:
            _raise_api_error(resp)
        return _decode_response_image(resp.json())
