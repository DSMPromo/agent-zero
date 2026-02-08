from python.helpers.api import ApiHandler, Request, Response

from python.helpers import settings

from typing import Any

import models

# Providers that don't need an API key (local/self-hosted)
_LOCAL_PROVIDERS = {"ollama", "lm_studio", "huggingface", "other"}

# Map of provider field → friendly name for warnings
_PROVIDER_FIELDS = {
    "chat_model_provider": "Chat Model",
    "util_model_provider": "Utility Model",
    "embed_model_provider": "Embedding Model",
    "browser_model_provider": "Browser Model",
}


def _check_missing_api_keys(s: dict) -> list[str]:
    """Check that cloud providers have API keys configured. Returns warning strings."""
    warnings = []
    api_keys = s.get("api_keys", {})

    for field, label in _PROVIDER_FIELDS.items():
        provider = s.get(field, "")
        if not provider or provider in _LOCAL_PROVIDERS:
            continue

        # Check settings api_keys dict first, then fall back to .env
        key = api_keys.get(f"api_key_{provider}", "")
        if not key:
            key = models.get_api_key(provider)

        if not key or key == "None":
            warnings.append(f"{label}: No API key found for provider \"{provider}\". Model calls will fail until a key is configured.")

    return warnings


class SetSettings(ApiHandler):
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        set = settings.convert_in(input)
        warnings = _check_missing_api_keys(set)
        set = settings.set_settings(set)
        result: dict[str, Any] = {"settings": set}
        if warnings:
            result["warnings"] = warnings
        return result
