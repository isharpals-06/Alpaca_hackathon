import sys
import os
sys.path.insert(0, os.path.abspath("."))

import httpx
from backend.config import settings

def test_alpaca_connection():
    print(f"Checking Alpaca credentials: Key ID present = {bool(settings.ALPACA_API_KEY)}, Base URL = {settings.ALPACA_BASE_URL}")
    if not settings.ALPACA_API_KEY or settings.ALPACA_API_KEY.startswith("your_"):
        print("[!] Alpaca API key is placeholder/not set in .env. (Offline mock fallback is active)")
        return False
    try:
        headers = {
            "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{settings.ALPACA_BASE_URL}/v2/account", headers=headers)
            if resp.is_success:
                acc = resp.json()
                print(f"[OK] Alpaca Paper Account connected successfully! Status: {acc.get('status')}, Buying Power: ${acc.get('buying_power')}, Cash: ${acc.get('cash')}")
                return True
            else:
                print(f"[!] Alpaca returned status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"[!] Alpaca connection error: {e}")
        return False

def test_openrouter_connection():
    print(f"Checking OpenRouter credentials: Key present = {bool(settings.OPENROUTER_API_KEY)}, Model = {settings.DEFAULT_LLM_MODEL}")
    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("your_"):
        print("[!] OpenRouter API key is placeholder/not set in .env.")
        return False
    try:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.DEFAULT_LLM_MODEL,
            "messages": [{"role": "user", "content": "Respond with 'OPENROUTER_OK' only."}],
            "max_tokens": 10,
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)
            if resp.is_success:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                print(f"[OK] OpenRouter test call succeeded! Response: {content}")
                return True
            else:
                print(f"[!] OpenRouter returned status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"[!] OpenRouter connection error: {e}")
        return False

if __name__ == "__main__":
    alpaca_ok = test_alpaca_connection()
    openrouter_ok = test_openrouter_connection()
    print(f"\n--- Summary: Alpaca: {'READY' if alpaca_ok else 'PENDING/MOCK'}, OpenRouter: {'READY' if openrouter_ok else 'PENDING'} ---")
