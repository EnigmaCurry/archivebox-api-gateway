import os
import aiohttp
import asyncio
import base64


class ConfigError(Exception):
    pass


def get_config():
    """Get config from environment variables"""
    cfg = {"headers": {}}

    def load_var(var, default=None):
        val = os.getenv(var, default)
        if val is not None:
            cfg[var] = val
        return val

    def require_var(var):
        val = load_var(var)
        if var not in cfg:
            raise ConfigError(f"Missing required environment variable: {var}")
        return val

    def basic_auth_token(username, password, encoding="utf-8"):
        return base64.b64encode(bytes(f"{username}:{password}", encoding)).decode(
            encoding
        )

    ## Secret key for hashing URLs:
    require_var("SECRET_KEY")
    ## Frontend:
    require_var("API_BASE_URL")
    load_var("PREFIX_PATH", "")
    ## Backend:
    require_var("ARCHIVEBOX_BASE_URL")
    require_var("ARCHIVEBOX_USERNAME")
    require_var("ARCHIVEBOX_PASSWORD")

    ## Optional HTTP Basic Authentication for the archivebox backend:
    backend_basic_auth_username = load_var("ARCHIVEBOX_BASIC_AUTH_USERNAME")
    backend_basic_auth_password = load_var("ARCHIVEBOX_BASIC_AUTH_PASSWORD")
    if (
        backend_basic_auth_username is not None
        and backend_basic_auth_password is not None
    ):
        token = basic_auth_token(
            backend_basic_auth_username, backend_basic_auth_password
        )
        cfg["headers"]["Authorization"] = f"Basic {token}"

    return cfg


config = get_config()
