import base64
import os
import time
from pathlib import Path
from typing import Dict, Optional

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from mcp_server_browser_use.utils.llm import DeepSeekR1ChatOllama, DeepSeekR1ChatOpenAI

PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI",
    "azure_openai": "Azure OpenAI",
    "anthropic": "Anthropic",
    "deepseek": "DeepSeek",
    "google": "Google",
    "alibaba": "Alibaba",
    "moonshot": "MoonShot",
    "unbound": "Unbound AI",
    "openrouter": "OpenRouter",
}


def get_llm_model(provider: str, **kwargs):
    """
    获取LLM 模型
    :param provider: 模型类型
    :param kwargs:
    :return:
    """
    if provider not in ["ollama"]:
        env_var = f"{provider.upper()}_API_KEY"
        api_key = kwargs.get("api_key", "") or os.getenv(env_var, "")
        if not api_key:
            raise MissingAPIKeyError(provider, env_var)
        kwargs["api_key"] = api_key

    if provider == "anthropic":
        if not kwargs.get("base_url", ""):
            base_url = "https://api.anthropic.com"
        else:
            base_url = kwargs.get("base_url")

        return ChatAnthropic(
            model=kwargs.get("model_name", "claude-3-5-sonnet-20241022"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=base_url,
            api_key=api_key,
        )
    elif provider == "mistral":
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("MISTRAL_ENDPOINT", "https://api.mistral.ai/v1")
        else:
            base_url = kwargs.get("base_url")
        if not kwargs.get("api_key", ""):
            api_key = os.getenv("MISTRAL_API_KEY", "")
        else:
            api_key = kwargs.get("api_key")

        return ChatMistralAI(
            model=kwargs.get("model_name", "mistral-large-latest"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=base_url,
            api_key=api_key,
        )
    elif provider == "openai":
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
        else:
            base_url = kwargs.get("base_url")

        return ChatOpenAI(
            model=kwargs.get("model_name", "gpt-4o"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=base_url,
            api_key=api_key,
        )
    elif provider == "deepseek":
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("DEEPSEEK_ENDPOINT", "")
        else:
            base_url = kwargs.get("base_url")

        if kwargs.get("model_name", "deepseek-chat") == "deepseek-reasoner":
            return DeepSeekR1ChatOpenAI(
                model=kwargs.get("model_name", "deepseek-reasoner"),
                temperature=kwargs.get("temperature", 0.0),
                base_url=base_url,
                api_key=api_key,
            )
        else:
            return ChatOpenAI(
                model=kwargs.get("model_name", "deepseek-chat"),
                temperature=kwargs.get("temperature", 0.0),
                base_url=base_url,
                api_key=api_key,
            )
    elif provider == "google":
        return ChatGoogleGenerativeAI(
            model=kwargs.get("model_name", "gemini-2.0-flash-exp"),
            temperature=kwargs.get("temperature", 0.0),
            api_key=api_key,
        )
    elif provider == "ollama":
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        else:
            base_url = kwargs.get("base_url")

        if "deepseek-r1" in kwargs.get("model_name", "qwen2.5:7b"):
            return DeepSeekR1ChatOllama(
                model=kwargs.get("model_name", "deepseek-r1:14b"),
                temperature=kwargs.get("temperature", 0.0),
                num_ctx=kwargs.get("num_ctx", 32000),
                base_url=base_url,
            )
        else:
            return ChatOllama(
                model=kwargs.get("model_name", "qwen2.5:7b"),
                temperature=kwargs.get("temperature", 0.0),
                num_ctx=kwargs.get("num_ctx", 32000),
                num_predict=kwargs.get("num_predict", 1024),
                base_url=base_url,
            )
    elif provider == "azure_openai":
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        else:
            base_url = kwargs.get("base_url")
        api_version = kwargs.get("api_version", "") or os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        return AzureChatOpenAI(
            model=kwargs.get("model_name", "gpt-4o"),
            temperature=kwargs.get("temperature", 0.0),
            api_version=api_version,
            azure_endpoint=base_url,
            api_key=api_key,
        )
    elif provider == "alibaba":
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("ALIBABA_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        else:
            base_url = kwargs.get("base_url")

        return ChatOpenAI(
            model=kwargs.get("model_name", "qwen-plus"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=base_url,
            api_key=api_key,
        )
    elif provider == "moonshot":
        return ChatOpenAI(
            model=kwargs.get("model_name", "moonshot-v1-32k-vision-preview"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=os.getenv("MOONSHOT_ENDPOINT"),
            api_key=os.getenv("MOONSHOT_API_KEY"),
        )
    elif provider == "unbound":
        return ChatOpenAI(
            model=kwargs.get("model_name", "gpt-4o-mini"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=os.getenv("UNBOUND_ENDPOINT", "https://api.getunbound.ai"),
            api_key=api_key,
        )
    elif provider == "openrouter":
        # OpenRouter uses OpenAI-compatible API, but requires custom endpoint and headers
        if not kwargs.get("base_url", ""):
            base_url = os.getenv("OPENROUTER_ENDPOINT", "https://openrouter.ai/api/v1")
        else:
            base_url = kwargs.get("base_url")
        # Use MCP_API_KEY if set, else OPENROUTER_API_KEY
        api_key = kwargs.get("api_key", "") or os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            raise MissingAPIKeyError("openrouter", "OPENROUTER_API_KEY")
        # OpenRouter requires HTTP-Referer and X-Title headers
        default_headers = {
            "HTTP-Referer": os.getenv("OPENROUTER_REFERER", "https://github.com/browser-use/mcp-browser-use"),
            "X-Title": os.getenv("OPENROUTER_X_TITLE", "MCP Browser Use"),
        }
        return ChatOpenAI(
            model=kwargs.get("model_name", "anthropic/claude-3.7-sonnet"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=base_url,
            api_key=api_key,
            default_headers=default_headers,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# Predefined model names for common providers
model_names = {
    "anthropic": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
    ],
    "openai": ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "o3-mini"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "google": [
        "gemini-2.0-flash",
        "gemini-2.0-flash-thinking-exp",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b-latest",
        "gemini-2.0-flash-thinking-exp-01-21",
        "gemini-2.0-pro-exp-02-05",
    ],
    "ollama": [
        "qwen2.5:7b",
        "qwen2.5:14b",
        "qwen2.5:32b",
        "qwen2.5-coder:14b",
        "qwen2.5-coder:32b",
        "llama2:7b",
        "deepseek-r1:14b",
        "deepseek-r1:32b",
    ],
    "azure_openai": ["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
    "mistral": [
        "pixtral-large-latest",
        "mistral-large-latest",
        "mistral-small-latest",
        "ministral-8b-latest",
    ],
    "alibaba": ["qwen-plus", "qwen-max", "qwen-turbo", "qwen-long"],
    "moonshot": ["moonshot-v1-32k-vision-preview", "moonshot-v1-8k-vision-preview"],
    "unbound": ["gemini-2.0-flash", "gpt-4o-mini", "gpt-4o", "gpt-4.5-preview"],
    "openrouter": [
        "google/gemini-2.5-pro-exp-03-25:free",
        "openai/gpt-3.5-turbo",
        "openai/gpt-4o",
        "mistralai/mistral-large",
        "meta-llama/llama-3-70b-instruct",
    ],
}


import time
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    A rate limiter that respects the REQUESTS_PER_MINUTE environment variable.
    Provides both synchronous and asynchronous interfaces.
    When REQUESTS_PER_MINUTE is not specified, no rate limiting is applied.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RateLimiter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._request_times = []
        
        # Check if REQUESTS_PER_MINUTE is explicitly set in environment
        requests_per_minute_env = os.getenv("REQUESTS_PER_MINUTE")
        self._rate_limiting_enabled = requests_per_minute_env is not None
        
        # Parse the value if set, otherwise we won't use it (unlimited)
        if self._rate_limiting_enabled:
            self._requests_per_minute = int(requests_per_minute_env)
            logger.info(f"Rate limiter initialized with {self._requests_per_minute} requests per minute")
        else:
            self._requests_per_minute = None
            logger.info("Rate limiter initialized with no limit (unlimited requests)")
            
        self._lock = asyncio.Lock()
    
    def _clean_old_requests(self):
        """Remove request timestamps older than 1 minute"""
        # Only clean if rate limiting is enabled
        if not self._rate_limiting_enabled:
            return
            
        now = datetime.now()
        self._request_times = [t for t in self._request_times if now - t < timedelta(minutes=1)]
    
    async def acquire(self):
        """
        Asynchronously wait until a request can be made according to the rate limit.
        If rate limiting is disabled, this returns immediately.
        """
        # Fast path if rate limiting is disabled
        if not self._rate_limiting_enabled:
            return
            
        async with self._lock:
            while True:
                self._clean_old_requests()
                if len(self._request_times) < self._requests_per_minute:
                    self._request_times.append(datetime.now())
                    return
                
                # Calculate sleep time
                oldest_allowed = datetime.now() - timedelta(minutes=1)
                if self._request_times:
                    sleep_time = (self._request_times[0] - oldest_allowed).total_seconds()
                    if sleep_time > 0:
                        logger.debug(f"Rate limit hit, waiting {sleep_time:.2f} seconds")
                        await asyncio.sleep(sleep_time + 0.1)  # Add a small buffer
                    else:
                        # No need to wait, but we need to re-check the conditions
                        continue
                else:
                    # No request times recorded, no need to wait
                    self._request_times.append(datetime.now())
                    return
    
    def acquire_sync(self):
        """
        Synchronously wait until a request can be made according to the rate limit.
        If rate limiting is disabled, this returns immediately.
        """
        # Fast path if rate limiting is disabled
        if not self._rate_limiting_enabled:
            return
            
        while True:
            # We need to handle the lock synchronously
            self._clean_old_requests()
            if len(self._request_times) < self._requests_per_minute:
                self._request_times.append(datetime.now())
                return
            
            # Calculate sleep time
            oldest_allowed = datetime.now() - timedelta(minutes=1)
            if self._request_times:
                sleep_time = (self._request_times[0] - oldest_allowed).total_seconds()
                if sleep_time > 0:
                    logger.debug(f"Rate limit hit, waiting {sleep_time:.2f} seconds")
                    time.sleep(sleep_time + 0.1)  # Add a small buffer
                else:
                    # We can remove the oldest request and continue
                    self._request_times.pop(0)
            else:
                # No request times recorded, no need to wait
                self._request_times.append(datetime.now())
                return


class MissingAPIKeyError(Exception):
    """Custom exception for missing API key."""

    def __init__(self, provider: str, env_var: str):
        provider_display = PROVIDER_DISPLAY_NAMES.get(provider, provider.upper())
        super().__init__(f"💥 {provider_display} API key not found! 🔑 Please set the " f"`{env_var}` environment variable or provide it in the UI.")


def encode_image(img_path):
    if not img_path:
        return None
    with open(img_path, "rb") as fin:
        image_data = base64.b64encode(fin.read()).decode("utf-8")
    return image_data


def get_latest_files(directory: str, file_types: list = [".webm", ".zip"]) -> Dict[str, Optional[str]]:
    """Get the latest recording and trace files"""
    latest_files: Dict[str, Optional[str]] = {ext: None for ext in file_types}

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return latest_files

    for file_type in file_types:
        try:
            matches = list(Path(directory).rglob(f"*{file_type}"))
            if matches:
                latest = max(matches, key=lambda p: p.stat().st_mtime)
                # Only return files that are complete (not being written)
                if time.time() - latest.stat().st_mtime > 1.0:
                    latest_files[file_type] = str(latest)
        except Exception as e:
            print(f"Error getting latest {file_type} file: {e}")

    return latest_files


async def capture_screenshot(browser_context):
    """Capture and encode a screenshot"""
    # Extract the Playwright browser instance
    playwright_browser = browser_context.browser.playwright_browser  # Ensure this is correct.

    # Check if the browser instance is valid and if an existing context can be reused
    if playwright_browser and playwright_browser.contexts:
        playwright_context = playwright_browser.contexts[0]
    else:
        return None

    # Access pages in the context
    pages = None
    if playwright_context:
        pages = playwright_context.pages

    # Use an existing page or create a new one if none exist
    if pages:
        active_page = pages[0]
        for page in pages:
            if page.url != "about:blank":
                active_page = page
    else:
        return None

    # Take screenshot
    try:
        screenshot = await active_page.screenshot(type="jpeg", quality=75, scale="css")
        encoded = base64.b64encode(screenshot).decode("utf-8")
        return encoded
    except Exception:
        return None
