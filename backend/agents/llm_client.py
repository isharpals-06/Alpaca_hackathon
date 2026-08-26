import json
import logging
from typing import Dict, Any, Type, TypeVar, Optional
import httpx
from pydantic import BaseModel

from backend.config import settings

logger = logging.getLogger("backend.llm")

T = TypeVar("T", bound=BaseModel)

class OpenRouterClient:
    """
    Resilient client for OpenRouter LLM completions with structured Pydantic output parsing.
    """

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        self.default_model = settings.DEFAULT_LLM_MODEL or "deepseek/deepseek-chat"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/isharpals-06/Alpaca_hackathon",
            "X-Title": "Alpaca AI Options Engine",
        }

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_retries: int = 2,
    ) -> T:
        """
        Sends a prompt to OpenRouter and parses the response into the specified Pydantic model.
        """
        target_model = model or self.default_model

        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        enriched_system_prompt = (
            f"{system_prompt}\n\n"
            f"IMPORTANT: You MUST respond ONLY with a single valid JSON object that strictly adheres to this JSON schema:\n"
            f"{schema_json}\n"
            f"Do NOT include explanations outside the JSON. Do not wrap in markdown quotes if possible, or use standard ```json ... ```."
        )

        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": enriched_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=35.0) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self._get_headers(),
                        json=payload,
                    )
                    
                    if not resp.is_success:
                        error_detail = resp.text
                        logger.warning(
                            "OpenRouter error (attempt %d/%d): status %d, detail: %s",
                            attempt + 1, max_retries + 1, resp.status_code, error_detail
                        )
                        raise ValueError(f"OpenRouter HTTP {resp.status_code}: {error_detail}")

                    raw_text = resp.json()["choices"][0]["message"]["content"].strip()
                    cleaned_json = self._clean_json_text(raw_text)
                    parsed_dict = json.loads(cleaned_json)
                    return response_model(**parsed_dict)

            except Exception as ex:
                last_error = ex
                logger.warning("Attempt %d failed to parse structured output: %s", attempt + 1, ex)
                if attempt == max_retries:
                    break

        raise RuntimeError(f"Failed to generate structured output after {max_retries + 1} attempts: {last_error}")

    def _clean_json_text(self, text: str) -> str:
        """Strips markdown code fences and extraneous text surrounding json."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        
        # Locate the outer JSON bounds { ... }
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            text = text[start_idx : end_idx + 1]
        return text

# Singleton instance
llm_client = OpenRouterClient()
