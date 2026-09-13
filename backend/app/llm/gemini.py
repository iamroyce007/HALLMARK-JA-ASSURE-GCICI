"""HALLMARK — Gemini LLM Client.
Async wrapper for Google Gemini with structured output, fallback to demo mode.
"""
import os, json, logging
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("hallmark.llm")

_HAS_GENAI = False
_client = None

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    logger.warning("google-generativeai not installed")

def _get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY", "")
        if key and _HAS_GENAI:
            genai.configure(api_key=key)
            _client = genai
    return _client

def is_live() -> bool:
    return bool(os.getenv("GEMINI_API_KEY")) and _HAS_GENAI

async def generate(
    prompt: str,
    system_instruction: str = "",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    response_json: bool = False,
) -> dict:
    """Generate text with Gemini. Returns {text, model, is_live, tokens}."""
    client = _get_client()
    if client and is_live():
        try:
            config = {"temperature": temperature, "max_output_tokens": max_tokens}
            if response_json:
                config["response_mime_type"] = "application/json"
            model_obj = client.GenerativeModel(
                model,
                system_instruction=system_instruction or None,
                generation_config=config,
            )
            response = model_obj.generate_content(prompt)
            text = response.text if response.text else ""
            usage = {}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                }
            return {"text": text, "model": model, "is_live": True, "tokens": usage}
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {"text": f"[DEMO FALLBACK — Gemini error: {str(e)[:100]}]", "model": "demo", "is_live": False, "tokens": {}}
    else:
        return {"text": "[DEMO FALLBACK — No Gemini API key configured]", "model": "demo", "is_live": False, "tokens": {}}

async def generate_json(
    prompt: str,
    system_instruction: str = "",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.2,
) -> dict:
    """Generate structured JSON output from Gemini."""
    result = await generate(prompt, system_instruction, model, temperature, response_json=True)
    if result["is_live"]:
        try:
            text = result["text"].strip()
            # Handle markdown code fences
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text
                text = text.rsplit("```", 1)[0]
            parsed = json.loads(text)
            return {"data": parsed, "model": result["model"], "is_live": True, "tokens": result["tokens"]}
        except json.JSONDecodeError:
            return {"data": {"raw_text": result["text"]}, "model": result["model"], "is_live": True, "tokens": result["tokens"]}
    return {"data": {}, "model": "demo", "is_live": False, "tokens": {}}

async def embed_text(text: str) -> list[float]:
    """Generate embedding vector for correction memory. Falls back to simple hash-based embedding."""
    client = _get_client()
    if client and is_live():
        try:
            result = client.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding error: {e}")
    # Fallback: deterministic hash-based 64-dim embedding
    import hashlib, math
    vec = []
    for i in range(64):
        h = hashlib.md5(f"{text}_{i}".encode()).digest()
        val = int.from_bytes(h[:4], "little", signed=True) / (2**31)
        vec.append(val)
    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [round(v / norm, 6) for v in vec]

