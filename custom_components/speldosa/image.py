"""Cover images for the page.

Spotify covers are https and load in the browser directly. Music Assistant's own image proxy is plain http on
the local network, which an https Home Assistant page may not load, so those go through this signed view. Only
URLs the integration handed out are fetched (no open proxy).
"""

from __future__ import annotations

import hashlib
from datetime import timedelta
from http import HTTPStatus

from aiohttp import ClientError, web

from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.auth import async_sign_path
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import IMAGE_URL

MAX_BYTES = 2 * 1024 * 1024
CACHE_ITEMS = 300
SIGN_FOR = timedelta(days=1)


class ImageProxy:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._urls: dict[str, str] = {}
        self._cache: dict[str, tuple[bytes, str]] = {}

    def page_url(self, url: str | None, refresh_token_id: str | None) -> str | None:
        """The URL the page should use for an image."""
        if not url or url.startswith("https://"):
            return url
        if not url.startswith("http://"):
            return None
        token = hashlib.sha256(url.encode()).hexdigest()[:32]
        self._urls[token] = url
        return async_sign_path(self.hass, f"{IMAGE_URL}/{token}", SIGN_FOR, refresh_token_id=refresh_token_id)

    async def fetch(self, token: str) -> tuple[bytes, str] | None:
        if token in self._cache:
            return self._cache[token]
        url = self._urls.get(token)
        if url is None:
            return None
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url, timeout=15) as resp:
                ctype = resp.headers.get("Content-Type", "")
                if resp.status != 200 or not ctype.startswith("image/"):
                    return None
                body = await resp.content.read(MAX_BYTES + 1)
        except (ClientError, TimeoutError):
            return None
        if len(body) > MAX_BYTES:
            return None
        if len(self._cache) >= CACHE_ITEMS:
            self._cache.pop(next(iter(self._cache)))
        self._cache[token] = (body, ctype)
        return body, ctype


class ImageView(HomeAssistantView):
    url = IMAGE_URL + "/{token}"
    name = "api:speldosa:image"
    requires_auth = True

    def __init__(self, proxy: ImageProxy) -> None:
        self._proxy = proxy

    async def get(self, request: web.Request, token: str) -> web.Response:
        hit = await self._proxy.fetch(token)
        if hit is None:
            return web.Response(status=HTTPStatus.NOT_FOUND)
        body, ctype = hit
        return web.Response(body=body, content_type=ctype, headers={"Cache-Control": "private, max-age=86400"})
