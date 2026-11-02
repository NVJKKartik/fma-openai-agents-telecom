"""Runtime settings for the telecom care agent."""

import os
import sys

TEMPERATURE = 0.2
MAX_TURNS = 6
PORT = int(os.environ.get("PORT", "8080"))

# Fixed billing-system date so seeded data stays deterministic.
TODAY = "2026-11-10"


def require_env() -> dict:
    missing = [k for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL") if not os.environ.get(k)]
    if missing:
        sys.exit(f"Missing required environment variables: {', '.join(missing)}")
    return {k: os.environ[k] for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")}
