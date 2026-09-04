import json
import logging
import re
from typing import Dict, Any, Optional
import httpx

from backend.config import settings

logger = logging.getLogger("backend.agents.llm")

class LLMClient:
    """
    Unified OpenRouter / LLM client for AI Council Agents.
    Executes prompt completions with structured JSON parsing and robust offline fallbacks.
    """

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        self.model = settings.DEFAULT_LLM_MODEL or "deepseek/deepseek-chat"
        self.is_configured = bool(
            self.api_key
            and len(self.api_key) > 8
            and not self.api_key.startswith("your_")
        )

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://alpaca-ai.trading",
            "X-Title": "Alpaca AI Council",
            "Content-Type": "application/json",
        }

    async def call_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback_dict: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Sends system + user prompt to OpenRouter and returns structured JSON dictionary.
        Falls back safely to fallback_dict if offline or on error.
        """
        if not self.is_configured:
            logger.info("OpenRouter API key not configured. Using intelligent heuristic fallback.")
            return fallback_dict or {}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"{system_prompt}\n\nIMPORTANT: You must respond in valid JSON format only, matching the requested schema exactly with no surrounding explanation."},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )

                if resp.is_success:
                    data = resp.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    parsed = self._extract_json(content)
                    if parsed:
                        return parsed
                else:
                    logger.warning("OpenRouter API returned error %s: %s", resp.status_code, resp.text)
        except Exception as ex:
            logger.warning("Error during OpenRouter LLM call: %s", ex)

        return fallback_dict or {}

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts JSON object from response string, stripping markdown fences if present."""
        if not text:
            return None
        text = text.strip()

        # Direct JSON load
        try:
            return json.loads(text)
        except Exception:
            pass

        # Regex for markdown json block ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        # Search for first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                pass

        return None

llm_client = LLMClient()
