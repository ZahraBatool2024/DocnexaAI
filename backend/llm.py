"""Thin Groq client (OpenAI-compatible chat completions API)."""
import base64
import json
import os
import re
import time

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
FALLBACKS = [m.strip() for m in os.getenv("GROQ_FALLBACK_MODELS", "").split(",") if m.strip()]


def configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def _post(payload: dict, timeout: int) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY', '').strip()}",
        "Content-Type": "application/json",
    }
    resp = None
    for attempt in range(3):
        try:
            resp = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers, timeout=timeout)
        except requests.Timeout as exc:
            raise HTTPException(504, "The AI model took too long. Try again or use a faster model.") from exc
        except requests.RequestException as exc:
            raise HTTPException(503, "Could not reach Groq. Check your internet connection.") from exc
        if resp.status_code in (429, 500, 502, 503) and attempt < 2:
            try:
                wait = float(resp.headers.get("retry-after", 1.5 * (attempt + 1)))
            except ValueError:
                wait = 2
            time.sleep(min(wait, 8))
            continue
        break
    return resp


def chat(messages, *, schema=None, model=None, max_tokens=4000, timeout=90) -> str:
    """Return the assistant text. Tries json_schema -> json_object -> plain if a model
    rejects the response format, and walks through fallback models on failure."""
    if not configured():
        raise HTTPException(503, "GROQ_API_KEY is not set. Add it to your .env file and restart the server.")

    modes = [None]
    if schema:
        modes = [
            {"type": "json_schema", "json_schema": {"name": "result", "strict": False, "schema": schema}},
            {"type": "json_object"},
            None,
        ]

    last = None
    for name in [model or MODEL] + FALLBACKS:
        for mode in modes:
            payload = {"model": name, "messages": messages, "temperature": 0, "max_tokens": max_tokens}
            if mode:
                payload["response_format"] = mode
            last = _post(payload, timeout)
            if last.status_code == 200:
                try:
                    content = last.json()["choices"][0]["message"].get("content") or ""
                except (KeyError, IndexError, ValueError, TypeError) as exc:
                    raise HTTPException(502, "Groq returned an unexpected response.") from exc
                if content.strip():
                    return content
                continue
            if last.status_code == 400:
                continue  # unsupported response_format or bad model -> try next mode/model
            break  # 401/402/429/5xx: try the next model

    if last is None or last.status_code == 200:
        raise HTTPException(502, "Groq returned an empty answer. Try again.")
    try:
        detail = last.json().get("error", {}).get("message", "")
    except ValueError:
        detail = ""
    hints = {
        400: "Groq rejected the request (check the model name in .env).",
        401: "Groq rejected the API key.",
        404: "Groq model not found (check the model name in .env).",
        413: "The document is too large for this model's limits.",
        429: "Groq rate limit hit. Wait a few seconds.",
    }
    raise HTTPException(
        last.status_code if last.status_code in hints and last.status_code != 400 else 502,
        f"{hints.get(last.status_code, 'Groq error.')} {detail}".strip(),
    )


def parse_json(raw: str) -> dict:
    """Parse JSON even if the model wrapped it in code fences or prose."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    try:
        return json.loads(raw)
    except ValueError:
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(raw[start : end + 1])


def vision_ocr(png_bytes: bytes) -> str:
    """Transcribe an image with a Groq vision model (fallback when PaddleOCR is unavailable)."""
    data_url = "data:image/png;base64," + base64.b64encode(png_bytes).decode()
    return chat(
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe all text in this document exactly as written, in reading "
                        "order. Keep table rows on one line separated by ' | '. Output only the text.",
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        model=VISION_MODEL,
        max_tokens=4000,
        timeout=120,
    )
