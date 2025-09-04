import os
import sys
from pathlib import Path

import httpx
import pytest


# Ensure src/ is on sys.path for local imports (src layout project)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySubtitle.Providers.Custom.CustomClient import CustomClient  # noqa: E402
from PySubtitle.SubtitleError import TranslationImpossibleError  # noqa: E402


ROUTER_SERVER = "https://router.huggingface.co"
ENDPOINT = "/v1/chat/completions"
# The router does not accept the ':auto' provider selector, and the base model is not a chat model
MODEL = "LumiOpen/Llama-Poro-2-70B-Instruct"


def _get_hf_token() -> str | None:
    return os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")


@pytest.mark.integration
def test_hf_router_direct_chat_completion():
    """
    Direct smoke test against Hugging Face Router OpenAI-compatible chat endpoint.
    Skips if no token is configured.
    """
    token = _get_hf_token()
    if not token:
        pytest.skip("HUGGINGFACE_API_KEY / HF_TOKEN not set in environment")

    url = f"{ROUTER_SERVER}{ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Say 'ping'"}],
        "stream": False,
        "temperature": 0.0,
    }

    try:
        insecure = os.getenv("HF_INSECURE") == "1"
        resp = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=30.0,
            follow_redirects=True,
            verify=not insecure,
        )
    except Exception as e:
        pytest.fail(f"Direct router call raised exception: {type(e).__name__}: {e}")

    assert resp.status_code == 200, f"Unexpected status {resp.status_code}: {resp.text}"
    if not resp.content or resp.headers.get("Content-Length") == "0":
        pytest.fail(f"Empty response body. Status: {resp.status_code}; Headers: {dict(resp.headers)}")
    data = resp.json()
    choices = data.get("choices") or []
    assert len(choices) > 0, f"No choices in response: {data}"
    # Prefer message-based response; some providers may return 'text'
    text = None
    if choices and isinstance(choices[0], dict):
        msg = choices[0].get("message") or {}
        text = msg.get("content") or choices[0].get("text")
    assert isinstance(text, str) and len(text.strip()) > 0, f"Empty text in response: {data}"


@pytest.mark.integration
def test_custom_client_smoke_chat_completion():
    """
    Smoke test using the library's CustomClient with the router settings.
    Skips if no token is configured.
    """
    token = _get_hf_token()
    if not token:
        pytest.skip("HUGGINGFACE_API_KEY / HF_TOKEN not set in environment")

    settings = {
        "server_address": ROUTER_SERVER,
        "endpoint": ENDPOINT,
        "supports_conversation": True,
        "supports_system_messages": True,  # send instructions as a system role message (OpenAI-compatible)
        "api_key": token,
        "model": MODEL,
        "timeout": 60.0,
        "verify_ssl": os.getenv("HF_INSECURE") != "1",
        # keep defaults for max_tokens / max_completion_tokens (server may decide)
        "instructions": "You are a translation engine. Follow system and user instructions exactly and reply concisely.",
        "retry_instructions": "Fix any validation errors and try again.",
    }

    client = CustomClient(settings)

    class StubPrompt:
        def __init__(self):
            self.messages = [{"role": "user", "content": "Say 'ping'"}]
            self.content = None

    prompt = StubPrompt()

    try:
        resp = client._make_request(prompt, temperature=0.0)
    except TranslationImpossibleError as tie:
        pytest.fail(f"CustomClient TranslationImpossibleError: {tie}")
    except Exception as e:
        pytest.fail(f"CustomClient raised unexpected exception: {type(e).__name__}: {e}")

    assert resp is not None, "CustomClient returned None response"
    assert isinstance(resp, dict), f"CustomClient returned non-dict: {type(resp)}"
    assert "text" in resp and isinstance(resp["text"], str) and len(resp["text"].strip()) > 0, f"Invalid response: {resp}"
