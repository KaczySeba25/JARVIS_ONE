import os
import time
import json
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

class ModelRouter:
    """Simple priority-based model router with exponential backoff.

    Priority:
    1) Local gpt4all if available
    2) HuggingFace Inference API if HUGGINGFACE_API_KEY set
    3) OpenAI API if OPENAI_API_KEY set
    """

    def __init__(self, providers=None, max_retries=3):
        self.max_retries = max_retries
        self.providers = providers or self._detect_providers()

    def _detect_providers(self):
        prov = []
        try:
            import gpt4all
            prov.append("gpt4all")
        except Exception:
            pass
        if os.getenv("HUGGINGFACE_API_KEY"):
            prov.append("huggingface")
        if os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_V2"):
            prov.append("openai")
        return prov

    def ask(self, messages, temperature=0.7, max_tokens=800):
        last_exc = None
        for provider in self.providers:
            for attempt in range(self.max_retries):
                try:
                    if provider == "gpt4all":
                        return self._ask_gpt4all(messages, temperature, max_tokens)
                    if provider == "huggingface":
                        return self._ask_huggingface(messages, temperature, max_tokens)
                    if provider == "openai":
                        return self._ask_openai(messages, temperature, max_tokens)
                except Exception as e:
                    last_exc = e
                    backoff = (2 ** attempt) + 0.1
                    time.sleep(backoff)
                    continue
        raise RuntimeError(f"All providers failed: {last_exc}")

    def _messages_to_prompt(self, messages):
        # simple concatenation, preserves roles
        return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])

    def _ask_gpt4all(self, messages, temperature, max_tokens):
        try:
            from gpt4all import GPT4All
            prompt = self._messages_to_prompt(messages)
            m = GPT4All()
            resp = m.generate(prompt, max_tokens=max_tokens)
            return resp
        except Exception as e:
            raise

    def _ask_huggingface(self, messages, temperature, max_tokens):
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        if not hf_token:
            raise RuntimeError("HuggingFace token missing")
        prompt = self._messages_to_prompt(messages)
        headers = {"Authorization": f"Bearer {hf_token}"}
        url = os.getenv("HUGGINGFACE_URL") or "https://api-inference.huggingface.co/models/gpt2"
        data = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "temperature": temperature}}
        r = requests.post(url, headers=headers, json=data, timeout=60)
        r.raise_for_status()
        out = r.json()
        if isinstance(out, dict) and "error" in out:
            raise RuntimeError(out["error"])
        # The HF inference may return a list of generated texts
        if isinstance(out, list):
            return out[0].get("generated_text", str(out[0]))
        return str(out)

    def _ask_openai(self, messages, temperature, max_tokens):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_V2"))
            # Map messages to openai chat messages
            chat_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
            resp = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=chat_messages, temperature=temperature, max_tokens=max_tokens)
            return resp.choices[0].message.content
        except Exception as e:
            raise
