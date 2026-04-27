#!/usr/bin/env python3
"""
OpenAI / LiteLLM relay diagnostic test.

Usage:
  python test_openai_api.py --key sk-... --url https://relay.com/v1 --model gpt-image-2
  python test_openai_api.py           # reads from config.json
  python test_openai_api.py --model gpt-image-1   # override single field
"""
import json, sys, time, argparse
import requests

# ── 1. Args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Test OpenAI/LiteLLM image relay")
parser.add_argument("--key",   help="API key (overrides config.json)")
parser.add_argument("--url",   help="Base URL e.g. https://relay.com/v1")
parser.add_argument("--model", help="Model name")
args = parser.parse_args()

try:
    cfg = json.load(open("config.json"))
except FileNotFoundError:
    cfg = {}

BASE_URL = (args.url  or cfg.get("openai_base_url", "")).rstrip("/") or "https://api.openai.com/v1"
API_KEY  =  args.key  or cfg.get("openai_api_key",  "")
MODEL    =  args.model or cfg.get("openai_model",   "gpt-image-2")

if not API_KEY:
    print("[ERROR] No API key. Run:")
    print("  python test_openai_api.py --key sk-... --url https://relay.com/v1")
    sys.exit(1)

GEN_URL = BASE_URL + "/images/generations"
HDR = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print(f"Base URL : {BASE_URL}")
print(f"Endpoint : {GEN_URL}")
print(f"Model    : {MODEL}")
print(f"Key ends : ...{API_KEY[-8:]}")
print()

# ── 2. Helper ─────────────────────────────────────────────────────────────────
def send(label, payload, xfail=False):
    print(f"  payload: {json.dumps(payload, ensure_ascii=False)}")
    t0 = time.time()
    try:
        r = requests.post(GEN_URL, json=payload, headers=HDR, timeout=90)
        dt = time.time() - t0
        if r.status_code == 200:
            d = r.json().get("data", [{}])
            has_url = bool(d[0].get("url"))
            has_b64 = bool(d[0].get("b64_json") or d[0].get("b64"))
            print(f"  OK  {label} ({dt:.1f}s) url={has_url} b64={has_b64}")
            return True
        else:
            try:
                b = r.json()
                e = b.get("error") or {}
                code = e.get("code") or e.get("type") or b.get("code") or ""
                msg  = e.get("message") or b.get("message") or r.text[:250]
            except Exception:
                code, msg = "", r.text[:250]
            tag = "(expected block)" if xfail else ""
            print(f"  ERR {label} HTTP {r.status_code} ({dt:.1f}s) {tag}")
            if code: print(f"       code: {code}")
            print(f"       msg : {msg[:200]}")
            return False
    except Exception as ex:
        print(f"  EXC {label} {ex}")
        return False

# ── 3. Tests ──────────────────────────────────────────────────────────────────
print("--- T1: minimal neutral ---")
t1 = send("minimal", {"model": MODEL, "prompt": "a red apple on a white table"})

print("\n--- T2: with size ---")
t2 = send("size", {"model": MODEL, "prompt": "a red apple on a white table", "size": "1024x1024"})

print("\n--- T3: Chinese prompt ---")
t3 = send("zh", {"model": MODEL, "prompt": "\u4e00\u4e2a\u653e\u5728\u767d\u8272\u684c\u5b50\u4e0a\u7684\u82f9\u679c", "size": "1024x1024"})

print("\n--- T4: sci-fi safe (no weapon words) ---")
t4 = send("scifi-safe", {
    "model": MODEL,
    "prompt": "sleek futuristic spaceship in space, 4-view blueprint, anime OVA style, white background",
    "size": "1024x1024",
})

print("\n--- T5: mecha 'combat machine' (may be blocked) ---")
t5 = send("mecha", {
    "model": MODEL,
    "prompt": "4-view reference of a bare-frame bipedal combat machine, anime mecha style, white background, no text, cel-shaded",
    "size": "1024x1024",
})

print("\n--- T6: weapon keywords (expect block on gpt-image-2) ---")
t6 = send("weapons", {
    "model": MODEL,
    "prompt": "heavily armed battleship with missile launchers and gun turrets, military combat vessel",
    "size": "1024x1024",
}, xfail=True)

print("\n--- T7: quality=medium ---")
t7 = send("quality", {"model": MODEL, "prompt": "a red apple on a white table", "size": "1024x1024", "quality": "medium"})

print("\n--- T8: gpt-image-1 mecha (less strict filter) ---")
t8 = send("img1-mecha", {
    "model": "gpt-image-1",
    "prompt": "4-view reference of a bipedal mecha robot, anime style, white background, no text",
    "size": "1024x1024",
})

print("\n--- T9: dall-e-3 (legacy, response_format=url) ---")
t9 = send("dalle3", {"model": "dall-e-3", "prompt": "a red apple on a white table",
                      "n": 1, "response_format": "url", "size": "1024x1024"})

# ── 4. Summary ────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for lbl, ok in [("T1 minimal",t1),("T2 size",t2),("T3 zh",t3),("T4 scifi",t4),
                ("T5 mecha",t5),("T6 weapons",t6),("T7 quality",t7),
                ("T8 gpt-image-1",t8),("T9 dall-e-3",t9)]:
    print(f"  {'OK' if ok else '--'}  {lbl}")

print()
if t1 and t2:
    print("[PASS] Basic connectivity: relay is reachable.")
else:
    print("[FAIL] Basic connectivity failed. Check URL, key, relay status.")

if t4 and not t5:
    print("[INFO] Safe sci-fi OK but 'combat machine' blocked -> content filter.")
    print("       Recommendation: use gpt-image-1 or gpt-image-1-mini.")
    if t8: print("       gpt-image-1 passed mecha test -> switch to gpt-image-1.")
elif t5:
    print("[PASS] 'combat machine' prompt is allowed on this relay.")
elif not t1:
    print("[FAIL] Even minimal prompts fail -> not a content filter issue.")
