"""
Gemini API client helper for optional LLM reasoning.
"""

import os
import json
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


def load_dotenv(env_path: Optional[str] = None, override: bool = False) -> None:
    """Load environment variables from a .env file into os.environ."""
    if env_path is None:
        env_path = Path(__file__).resolve().parents[1] / ".env"
    else:
        env_path = Path(env_path)

    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            if override or key not in os.environ:
                os.environ[key] = value


class GeminiClient:
    """Minimal helper for Gemini text generation via API key."""

    DEFAULT_ENDPOINT = "https://gemini.googleapis.com/v1/models/text-bison-001:generateText"

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        if api_key is None:
            load_dotenv()
            api_key = os.environ.get("GEMINI_API_KEY")

        self.api_key = api_key
        self.endpoint = endpoint or os.environ.get("GEMINI_API_ENDPOINT") or self.DEFAULT_ENDPOINT

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, max_output_tokens: int = 256, temperature: float = 0.3) -> str:
        """Generate text from Gemini using a prompt."""
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        try:
            data = self._send_request(self.endpoint, prompt, max_output_tokens, temperature)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                for fallback in self._fallback_endpoints():
                    try:
                        data = self._send_request(fallback, prompt, max_output_tokens, temperature)
                        self.endpoint = fallback
                        break
                    except urllib.error.HTTPError as fallback_exc:
                        if fallback_exc.code == 404:
                            continue
                        raise
                else:
                    raise RuntimeError(f"Gemini endpoint not found: {self.endpoint}") from exc
            else:
                raise

        return self._extract_text(data)

    def _send_request(self, endpoint: str, prompt: str, max_output_tokens: int, temperature: float) -> dict:
        payload = self._build_payload(endpoint, prompt, max_output_tokens, temperature)

        url = endpoint
        separator = "?" if "?" not in url else "&"
        url = f"{url}{separator}key={urllib.parse.quote(self.api_key)}"

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)

    def _build_payload(self, endpoint: str, prompt: str, max_output_tokens: int, temperature: float) -> dict:
        if endpoint.endswith(":predict"):
            return {
                "instances": [{"content": prompt}],
                "parameters": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens
                }
            }

        return {
            "prompt": {"text": prompt},
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        }

    def _extract_text(self, data: dict) -> str:
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0].get("content", "").strip()
        if "response" in data and isinstance(data["response"], dict):
            outputs = data["response"].get("output", [])
            if outputs and isinstance(outputs, list) and outputs[0].get("content"):
                return outputs[0].get("content", "").strip()
        if "text" in data:
            return str(data["text"]).strip()
        if "predictions" in data and data["predictions"]:
            first = data["predictions"][0]
            if isinstance(first, dict):
                return str(first.get("content", first.get("text", ""))).strip()
            return str(first).strip()
        return json.dumps(data)[:2000]

    def _fallback_endpoints(self) -> list:
        candidates = [
            "https://gemini.googleapis.com/v1/models/text-bison-001:predict",
            "https://gemini.googleapis.com/v1beta2/models/text-bison-001:generateText",
            "https://gemini.googleapis.com/v1beta2/models/text-bison-001:predict",
            "https://gemini.googleapis.com/v1/models/text-bison@001:generateText",
            "https://gemini.googleapis.com/v1/models/text-bison@001:predict",
            "https://gemini.googleapis.com/v1/models/gemini-1.5:generateText",
            "https://gemini.googleapis.com/v1/models/gemini-1.5:predict",
            "https://gemini.googleapis.com/v1beta2/models/gemini-1.5:generateText",
            "https://gemini.googleapis.com/v1beta2/models/gemini-1.5:predict",
            "https://gemini.googleapis.com/v1/models/gemini-1.5@001:generateText",
            "https://gemini.googleapis.com/v1/models/gemini-1.5@001:predict",
        ]
        return [ep for ep in candidates if ep != self.endpoint]
