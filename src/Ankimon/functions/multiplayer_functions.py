"""Small client for the merged Ankimon multiplayer API."""
import json
import os

import requests
from aqt import mw

from ..resources import user_path_credentials


class MultiplayerClientError(Exception):
    """Raised when the multiplayer API cannot be reached or used."""


_session = requests.Session()
_credentials_cache = None


def _headers():
    global _credentials_cache
    try:
        mtime = os.stat(user_path_credentials).st_mtime_ns
    except OSError:
        mtime = None
    if _credentials_cache is not None and _credentials_cache[0] == mtime:
        username, api_key = _credentials_cache[1:]
    else:
        try:
            with open(user_path_credentials, "r", encoding="utf-8") as handle:
                credentials = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise MultiplayerClientError("Set up your Ankimon username and API key first.") from exc
        username = credentials.get("username")
        api_key = credentials.get("api_key")
        if not username or not api_key:
            raise MultiplayerClientError("Your Ankimon credentials are incomplete.")
        _credentials_cache = (mtime, username, api_key)
    return {
        "Authorization": f"Bearer {api_key}",
        "X-Ankimon-Username": username,
        "Content-Type": "application/json",
    }


def _request(method, path, body=None):
    base_url = mw.settings_obj.get("multiplayer.server_url", "http://localhost:8080").rstrip("/")
    try:
        response = _session.request(
            method, f"{base_url}{path}", headers=_headers(), json=body, timeout=10
        )
    except requests.exceptions.RequestException as exc:
        raise MultiplayerClientError(f"Couldn't reach the multiplayer server: {exc}") from exc
    try:
        payload = response.json()
    except ValueError as exc:
        raise MultiplayerClientError("The multiplayer server returned invalid JSON.") from exc
    if response.status_code >= 400:
        raise MultiplayerClientError(payload.get("error", f"Server error ({response.status_code})"))
    return payload


def get_state():
    return _request("GET", "/v1/state")


def challenge_bot(challenge_value):
    return _request("POST", "/v1/matches", {"opponent": challenge_value})

