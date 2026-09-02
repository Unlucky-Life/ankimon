"""Small client for the merged Ankimon multiplayer API."""
import json
import os
import time
import uuid

import requests
from aqt import mw

from ..resources import user_path_credentials


class MultiplayerClientError(Exception):
    """Raised when the multiplayer API cannot be reached or used."""


_session = requests.Session()
_credentials_cache = None
_pending_events = []
_active_pokemon = None
_batch_size = 5
_max_pending_events = 100


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


def submit_turn(match_id, move=None):
    body = {} if not move else {"move": move}
    return _request("POST", f"/v1/matches/{match_id}/turns", body)


def queue_review(reviewer_args, level, active_pokemon=None):
    """Queue one Anki review and flush in small batches.

    The hook intentionally does no network work for the common case: callers
    only get a state response when a batch is ready or a flush is requested.
    """
    if len(reviewer_args) >= 3:
        card = reviewer_args[1]
        ease = reviewer_args[2]
    else:
        card = None
        ease = 0
    card_id = getattr(card, "id", None) or uuid.uuid4().hex
    grade = {1: "again", 2: "hard", 3: "good", 4: "easy"}.get(int(ease), "good")
    global _active_pokemon
    if active_pokemon:
        _active_pokemon = {
            "name": str(active_pokemon.get("name", "")),
            "id": int(active_pokemon.get("id", 0)),
            "level": max(1, int(active_pokemon.get("level", level) or level or 1)),
        }
    _pending_events.append({
        "id": f"review-{card_id}-{time.time_ns()}-{uuid.uuid4().hex[:8]}",
        "type": "card_reviewed",
        "ts": str(int(time.time())),
        "grade": grade,
        "time_s": 0,
        "level": max(1, int(level or 1)),
    })
    if len(_pending_events) > _max_pending_events:
        del _pending_events[:-_max_pending_events]
    if len(_pending_events) >= _batch_size:
        return flush_reviews()
    return None


def flush_reviews():
    """Send queued reviews; failures leave no UI-facing exception."""
    if not _pending_events:
        return None
    events = list(_pending_events[:_max_pending_events])
    active_pokemon = _active_pokemon
    try:
        state = _request("POST", "/v1/events:batch", {
            "events": events,
            "active_pokemon": active_pokemon,
        })
        del _pending_events[:len(events)]
        return state
    except MultiplayerClientError:
        # Keep the stable IDs for a later flush. The cap prevents an offline
        # server from growing memory forever or delaying the reviewer.
        return None
