"""Prompt sanitizer for OpenAI gpt-image models.

Handles two distinct types of content that trigger gpt-image-2 guardrails:

1. ARTIST NAMES  ("in the style of X", "influenced by X")
   -> OpenAI copyright/similarity guardrail
   -> strips the phrase entirely

2. AMBIGUOUS TERMS  ("bust portrait", "teenager", etc.)
   -> content-safety or copyright-similarity guardrail
   -> replaces with unambiguous equivalents

Only called in the OpenAI pathway. Gemini prompts are NEVER passed through here.

Usage:
    from core.prompt_sanitizer import sanitize_for_openai
    clean_prompt = sanitize_for_openai(raw_prompt)
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Exact-string substitutions (case-sensitive, applied first)
# ---------------------------------------------------------------------------
# Each entry: (old, new)
# "bust portrait" / "bust shot": art-history terms that gpt-image-2 misreads
# as requesting explicit content when combined with female characters.
_SUBSTITUTIONS = [
    ("bust portrait", "head-and-shoulders portrait"),
    ("bust shot",     "portrait shot"),
]

# ---------------------------------------------------------------------------
# Regex patterns -- artist name removal
# ---------------------------------------------------------------------------
# Matches the exact templates produced by character_generator.py:
#   f"{style_line} strongly in the style of {artist_text}, "
#   f"character design and lineart influenced by {artist_text}."
# Also covers shorter manual forms.
_PATTERNS = [
    # "strongly in the style of <names>[,|.]"
    re.compile(
        r",?\s*strongly in the style of [^,\.!]+(,\.?|[,\.])?",
        re.IGNORECASE,
    ),
    # "in the style of <names>[,|.]"
    re.compile(
        r",?\s*in the style of [^,\.!]+(,\.?|[,\.])?",
        re.IGNORECASE,
    ),
    # "character design and lineart influenced by <names>[.]"
    re.compile(
        r",?\s*character design and lineart influenced by [^,\.!]+(\.)?",
        re.IGNORECASE,
    ),
    # "influenced by <names>[,|.]"
    re.compile(
        r",?\s*influenced by [^,\.!]+(,\.?|[,\.])?",
        re.IGNORECASE,
    ),
]


def sanitize_for_openai(prompt: str) -> str:
    """Sanitize *prompt* for OpenAI gpt-image models.

    Applies substitutions then strips artist-name phrases.
    Returns the cleaned prompt. Never modifies Gemini prompts.
    """
    for old, new in _SUBSTITUTIONS:
        prompt = prompt.replace(old, new)
    for pat in _PATTERNS:
        prompt = pat.sub("", prompt)

    # Clean up residual whitespace / punctuation
    prompt = re.sub(r"  +", " ", prompt).strip()
    prompt = re.sub(r",\s*\.", ".", prompt)
    prompt = re.sub(r",\s*$", "", prompt).strip()

    return prompt


# ---------------------------------------------------------------------------
# Quick self-test  (run: python -m core.prompt_sanitizer)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        # Artist name removal (character_generator format)
        (
            "Anime style strongly in the style of Studio Ghibli, "
            "character design and lineart influenced by Studio Ghibli. "
            "Young adult female, cheerful.",
            "Anime style Young adult female, cheerful.",
        ),
        # Manual "in the style of"
        (
            "A warrior woman in the style of Yoshitaka Amano, fantasy art.",
            "A warrior woman fantasy art.",
        ),
        # bust portrait substitution
        (
            "bust portrait, a teenager female character.",
            "head-and-shoulders portrait, a teenager female character.",
        ),
        # bust shot substitution
        (
            "bust shot of a female character.",
            "portrait shot of a female character.",
        ),
        # No changes needed
        (
            "A red apple on a white table.",
            "A red apple on a white table.",
        ),
    ]

    all_ok = True
    for raw, expected in samples:
        result = sanitize_for_openai(raw)
        ok = result == expected
        print(f"[{'OK' if ok else 'FAIL'}] {repr(raw[:60])} ...")
        if not ok:
            print(f"  expected : {repr(expected)}")
            print(f"  got      : {repr(result)}")
            all_ok = False

    print("\nAll tests passed." if all_ok else "\nSome tests FAILED.")
