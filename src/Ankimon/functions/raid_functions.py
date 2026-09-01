"""HTTP client for the raid-server relay (see raid-server/ at the repo root).

Follows the same shape as pyobj/ankimon_leaderboard.py: read credentials
from user_path_credentials, respect a settings toggle, use `requests`
directly, and surface failures via showInfo/logger instead of silently
swallowing them.
"""
import json

import requests
from aqt import mw
from aqt.utils import showInfo

from ..resources import user_path_credentials


class RaidClientError(Exception):
    """Raised when a raid-server request fails or credentials are missing."""


def _server_url():
    return mw.settings_obj.get("raid.server_url", "http://localhost:8080").rstrip("/")


def _auth_headers():
    try:
        with open(user_path_credentials, "r", encoding="utf-8") as f:
            credentials = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise RaidClientError(
            "No Ankimon credentials found. Set them up from the Ankimon menu "
            "(the same credentials used for the leaderboard) before joining a raid."
        )

    username = credentials.get("username")
    api_key = credentials.get("api_key")
    if not username or not api_key:
        raise RaidClientError(
            "Missing username/api_key in Ankimon credentials. Set them up from the Ankimon menu."
        )

    return username, {
        "X-Ankimon-Username": username,
        "X-Ankimon-Api-Key": api_key,
        "Content-Type": "application/json",
    }


def _request(method, path, json_body=None):
    if not mw.settings_obj.get("raid.enabled", False):
        raise RaidClientError("Raids are disabled. Enable them in Ankimon settings first.")

    _, headers = _auth_headers()
    url = f"{_server_url()}{path}"
    try:
        response = requests.request(method, url, headers=headers, json=json_body, timeout=10)
    except requests.exceptions.RequestException as e:
        raise RaidClientError(f"Couldn't reach the raid server at {url}: {e}")

    if response.status_code >= 400:
        try:
            detail = response.json().get("error", response.text)
        except ValueError:
            detail = response.text
        raise RaidClientError(f"Raid server error ({response.status_code}): {detail}")

    try:
        return response.json()
    except ValueError:
        raise RaidClientError("Raid server returned an unexpected (non-JSON) response.")


def create_raid(boss_name, boss_level, max_hp):
    """Create a new raid boss on the server. Returns the raid state dict."""
    return _request("POST", "/raids", {
        "boss_name": boss_name,
        "boss_level": boss_level,
        "max_hp": max_hp,
    })


def list_active_raids():
    """Return the list of raids whose boss hasn't been defeated yet."""
    return _request("GET", "/raids")


def poll_raid_state(raid_id):
    """Fetch the current state of one raid (boss HP, participants)."""
    return _request("GET", f"/raids/{raid_id}")


def join_raid(raid_id):
    # No "username" field in the body - the server takes the participant's
    # identity from the authenticated X-Ankimon-Username header, so a
    # request body can't claim to act as someone else.
    return _request("POST", f"/raids/{raid_id}/join", {})


def send_attack(raid_id, damage, level, base_power, atk_stat, def_stat):
    """Report a locally-computed hit against the raid boss.

    The server clamps `damage` to a plausibility ceiling derived from the
    other fields (see raid-server/damage.go) - it isn't trusted outright.
    Returns the server's response, whose `damage_accepted` field is what was
    actually applied.
    """
    return _request("POST", f"/raids/{raid_id}/attack", {
        "damage": int(damage),
        "level": int(level),
        "base_power": int(base_power),
        "atk_stat": int(atk_stat),
        "def_stat": int(def_stat),
    })


def try_send_attack(raid_id, damage, level, base_power, atk_stat, def_stat):
    """Best-effort version of send_attack() for the reviewer hot path.

    A raid hiccup shouldn't break the local solo-battle flow, so this logs
    and returns None instead of raising.
    """
    try:
        response = send_attack(raid_id, damage, level, base_power, atk_stat, def_stat)
        session = getattr(mw, "raid_session_obj", None)
        if session is not None:
            session.apply_state(response.get("raid", response))
            announce_completion(session)
        return response
    except RaidClientError as e:
        mw.logger.log_and_showinfo("error", f"Raid attack failed to sync: {e}")
        return None


def announce_completion(session):
    """Show one completion popup when a raid boss reaches zero HP."""
    notice = session.take_completion_notice()
    if not notice:
        return
    participants = notice.get("participants") or {}
    total_damage = sum(
        int(item.get("damage_dealt", 0))
        for item in participants.values()
        if isinstance(item, dict)
    )
    showInfo(
        f"{notice['boss_name']} was defeated!\n\n"
        f"Raid ID: {notice['raid_id']}\n"
        f"Team damage: {total_damage}"
    )


def show_bot_battle_result(opponent_name, won, pokemon_name=None):
    """Shared popup hook for the multiplayer bot battle client."""
    result = "Victory" if won else "Defeat"
    detail = f"\n{pokemon_name}" if pokemon_name else ""
    showInfo(f"{result} against {opponent_name}!{detail}")
