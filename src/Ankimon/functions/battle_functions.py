import copy
import json
from ..poke_engine import constants
from ..resources import move_names_file_path
from ..pyobj.error_handler import show_warning_with_traceback

with open(move_names_file_path, "r", encoding="utf-8") as f:
    MOVE_NAME_LOOKUP = json.load(f)

def format_move_name(move: str) -> str:
    """
    Look up the official move name using the normalized key.
    Falls back to title-casing with spaces if not found.
    """
    key = move.replace(" ", "").replace("-", "").replace("_", "").lower()
    return MOVE_NAME_LOOKUP.get(key, " ".join(word.capitalize() for word in move.replace("_", " ").split()))

def update_pokemon_battle_status(battle_info: dict, enemy_pokemon, main_pokemon):
    """
    Update Pokemon battle status and volatile status based on battle instructions.
    HP is now handled by the main battle loop to ensure a single source of truth.
    This function now only processes status changes.
    """
    if not isinstance(battle_info, dict) or 'instructions' not in battle_info:
        return False, False

    instructions = battle_info.get('instructions', [])
    if not instructions:
        return False, False

    enemy_status_changed = False
    main_status_changed = False

    try:
        # Initialize volatile_status sets if they don't exist
        if not hasattr(enemy_pokemon, 'volatile_status'):
            enemy_pokemon.volatile_status = set()
        if not hasattr(main_pokemon, 'volatile_status'):
            main_pokemon.volatile_status = set()

        for instr in instructions:
            # Skip malformed instructions or instructions this function doesn't handle
            if not isinstance(instr, (list, tuple)) or len(instr) < 2:
                continue

            action = instr[0]
            target = instr[1]

            # This function only handles status, not damage or heal
            if action in [constants.MUTATOR_DAMAGE, constants.MUTATOR_HEAL]:
                continue

            status_value = instr[2] if len(instr) >= 3 else None

            # Handle regular status application
            if action == constants.MUTATOR_APPLY_STATUS and status_value:
                if target == 'opponent':
                    if enemy_pokemon.battle_status != status_value:
                        enemy_pokemon.battle_status = status_value
                        enemy_status_changed = True
                elif target == 'user':
                    if main_pokemon.battle_status != status_value:
                        main_pokemon.battle_status = status_value
                        main_status_changed = True

            # Handle regular status removal
            elif action == constants.MUTATOR_REMOVE_STATUS:
                if target == 'opponent':
                    if enemy_pokemon.battle_status != 'fighting':
                        enemy_pokemon.battle_status = 'fighting'
                        enemy_status_changed = True
                elif target == 'user':
                    if main_pokemon.battle_status != 'fighting':
                        main_pokemon.battle_status = 'fighting'
                        main_status_changed = True

            # Handle volatile status application
            elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS and status_value:
                if target == 'opponent':
                    if status_value not in enemy_pokemon.volatile_status:
                        enemy_pokemon.volatile_status.add(status_value)
                        enemy_status_changed = True
                elif target == 'user':
                    if status_value not in main_pokemon.volatile_status:
                        main_pokemon.volatile_status.add(status_value)
                        main_status_changed = True

            # Handle volatile status removal
            elif action == constants.MUTATOR_REMOVE_VOLATILE_STATUS and status_value:
                if target == 'opponent':
                    if status_value in enemy_pokemon.volatile_status:
                        enemy_pokemon.volatile_status.discard(status_value)
                        enemy_status_changed = True
                elif target == 'user':
                    if status_value in main_pokemon.volatile_status:
                        main_pokemon.volatile_status.discard(status_value)
                        main_status_changed = True

        # Final check for fainted status based on the already-updated HP from the main loop
        if hasattr(enemy_pokemon, 'hp') and enemy_pokemon.hp <= 0:
            if enemy_pokemon.battle_status != 'fainted':
                enemy_pokemon.battle_status = 'fainted'
                enemy_pokemon.volatile_status = set() # Clear volatiles on faint
                enemy_status_changed = True

        if hasattr(main_pokemon, 'hp') and main_pokemon.hp <= 0:
            if main_pokemon.battle_status != 'fainted':
                main_pokemon.battle_status = 'fainted'
                main_pokemon.volatile_status = set() # Clear volatiles on faint
                main_status_changed = True

        return enemy_status_changed, main_status_changed

    except Exception as e:
        # Use the existing error handler if available, otherwise print
        try:
            from ..pyobj.error_handler import show_warning_with_traceback
            show_warning_with_traceback(e, "Failed to update pokemon battle status")
        except ImportError:
            print(f"ERROR in update_pokemon_battle_status: {e}")
        return False, False


def _process_battle_effects(
    instructions: list,  # Keep for compatibility but won't use
    translator,
    main_pokemon=None,
    enemy_pokemon=None,
    current_state=None,
    changes=None
) -> list:
    """
    Process battle changes with Pokemon names and persistent effect messages.
    This version uses the changes variable instead of instructions to generate messages.
    """
    if not changes or not isinstance(changes, list):
        return []

    effect_messages = []

    def get_pokemon_name(target_side: str) -> str:
        if target_side == 'user':
            return main_pokemon.name.capitalize() if (main_pokemon and hasattr(main_pokemon, 'name')) else "Your Pokemon"
        else:
            return enemy_pokemon.name.capitalize() if (enemy_pokemon and hasattr(enemy_pokemon, 'name')) else "Enemy Pokemon"

    def normalize_status_name(status_name: str) -> str:
        return status_name.lower().replace('_', '').replace(' ', '').replace('-', '')

    def safe_translate(key: str, **kwargs) -> str:
        try:
            if translator:
                result = translator.translate(key, **kwargs)
                if result and result.strip():
                    return result
        except (KeyError, AttributeError, Exception) as e:
            print(f"Translation error for key '{key}': {e}")

        if 'pokemon_name' in kwargs and 'status_name' in kwargs:
            if 'apply' in key or 'still' in key:
                return f"{kwargs['pokemon_name']} is affected by {kwargs['status_name']}!"
            elif 'remove' in key:
                return f"{kwargs['pokemon_name']} recovers from {kwargs['status_name']}!"
        return f"Battle effect: {key}"

    # Track newly applied statuses/volatiles from changes
    newly_applied_statuses = set()
    newly_applied_volatiles = set()

    # First pass: identify newly applied effects
    for change in changes:
        key = change['key']
        before = change['before']
        after = change['after']

        # Track status applications
        if key.endswith('.status') and before in ('fighting', None) and after not in ('fighting', None):
            target = 'user' if key.startswith('user.') else 'opponent'
            newly_applied_statuses.add((target, normalize_status_name(after)))

        # Track volatile status applications
        elif key.endswith('.volatile_status') and isinstance(after, set) and isinstance(before, set):
            target = 'user' if key.startswith('user.') else 'opponent'
            new_volatiles = after - before if before else after
            for volatile in new_volatiles:
                newly_applied_volatiles.add((target, normalize_status_name(volatile)))

    def check_persistent_effects():
        """Check for ongoing effects, but skip fainted Pokemon and newly applied statuses."""
        persistent_messages = []

        # Weather (unaffected by fainted status)
        if current_state and hasattr(current_state, 'weather') and current_state.weather:
            weather_key = f"weather_{normalize_status_name(current_state.weather)}_still"
            weather_message = safe_translate(
                weather_key,
                weather=current_state.weather.replace('-', ' ').title()
            )
            persistent_messages.append(weather_message)

        # Status for main Pokemon
        if main_pokemon and getattr(main_pokemon, 'battle_status', None) not in ('fighting', 'fainted', None):
            norm_status = normalize_status_name(main_pokemon.battle_status)
            if ('user', norm_status) not in newly_applied_statuses:
                status_key = f"status_{norm_status}_still"
                status_message = safe_translate(
                    status_key,
                    pokemon_name=main_pokemon.name.capitalize(),
                    status_name=main_pokemon.battle_status.replace('_', ' ').title()
                )
                persistent_messages.append(status_message)

        # Status for enemy Pokemon
        if enemy_pokemon and getattr(enemy_pokemon, 'battle_status', None) not in ('fighting', 'fainted', None):
            norm_status = normalize_status_name(enemy_pokemon.battle_status)
            if ('opponent', norm_status) not in newly_applied_statuses:
                status_key = f"status_{norm_status}_still"
                status_message = safe_translate(
                    status_key,
                    pokemon_name=enemy_pokemon.name.capitalize(),
                    status_name=enemy_pokemon.battle_status.replace('_', ' ').title()
                )
                persistent_messages.append(status_message)

        # Volatile for main Pokemon
        if main_pokemon and getattr(main_pokemon, 'battle_status', None) != 'fainted' and hasattr(main_pokemon, 'volatile_status') and main_pokemon.volatile_status:
            for volatile_status in main_pokemon.volatile_status:
                norm_volatile = normalize_status_name(volatile_status)
                if ('user', norm_volatile) not in newly_applied_volatiles:
                    volatile_key = f"volatile_{norm_volatile}_still"
                    volatile_message = safe_translate(
                        volatile_key,
                        pokemon_name=main_pokemon.name.capitalize(),
                        status_name=volatile_status.replace('_', ' ').title()
                    )
                    persistent_messages.append(volatile_message)

        # Volatile for enemy Pokemon
        if enemy_pokemon and getattr(enemy_pokemon, 'battle_status', None) != 'fainted' and hasattr(enemy_pokemon, 'volatile_status') and enemy_pokemon.volatile_status:
            for volatile_status in enemy_pokemon.volatile_status:
                norm_volatile = normalize_status_name(volatile_status)
                if ('opponent', norm_volatile) not in newly_applied_volatiles:
                    volatile_key = f"volatile_{norm_volatile}_still"
                    volatile_message = safe_translate(
                        volatile_key,
                        pokemon_name=enemy_pokemon.name.capitalize(),
                        status_name=volatile_status.replace('_', ' ').title()
                    )
                    persistent_messages.append(volatile_message)

        return persistent_messages

    # Add persistent effect messages first
    if current_state and (main_pokemon or enemy_pokemon):
        effect_messages.extend(check_persistent_effects())

    # Process changes to generate messages
    for change in changes:
        try:
            key = change['key']
            before = change['before']
            after = change['after']

            # Skip if no actual change
            if before == after:
                continue

            # Handle status changes
            if key.endswith('.status'):
                target = 'user' if key.startswith('user.') else 'opponent'
                pokemon_name = get_pokemon_name(target)

                # Status applied
                if before in ('fighting', None) and after not in ('fighting', None):
                    normalized_status = normalize_status_name(after)
                    translation_key = f"status_{normalized_status}_apply"

                    if after.lower() in constants.KNOWN_REGULAR_STATUSES:
                        message = safe_translate(
                            translation_key,
                            pokemon_name=pokemon_name,
                            status_name=after.replace('_', ' ').title()
                        )
                    else:
                        status_name = after.replace('_', ' ').title()
                        message = safe_translate(
                            "status_unknown_apply",
                            pokemon_name=pokemon_name,
                            status_name=status_name
                        )
                    effect_messages.append(message)

                # Status removed
                elif before not in ('fighting', None) and after in ('fighting', None):
                    normalized_status = normalize_status_name(before)
                    translation_key = f"status_{normalized_status}_remove"

                    if before.lower() in constants.KNOWN_REGULAR_STATUSES:
                        message = safe_translate(
                            translation_key,
                            pokemon_name=pokemon_name,
                            status_name=before.replace('_', ' ').title()
                        )
                    else:
                        status_name = before.replace('_', ' ').title()
                        message = safe_translate(
                            "status_unknown_remove",
                            pokemon_name=pokemon_name,
                            status_name=status_name
                        )
                    effect_messages.append(message)

            # Handle volatile status changes
            elif key.endswith('.volatile_status'):
                target = 'user' if key.startswith('user.') else 'opponent'
                pokemon_name = get_pokemon_name(target)

                if isinstance(after, set) and isinstance(before, set):
                    # New volatile statuses added
                    added_volatiles = after - before if before else after
                    for volatile_status in added_volatiles:
                        normalized_status = normalize_status_name(volatile_status)
                        translation_key = f"volatile_{normalized_status}_apply"

                        if normalized_status in constants.KNOWN_VOLATILE_STATUSES:
                            message = safe_translate(
                                translation_key,
                                pokemon_name=pokemon_name,
                                status_name=volatile_status.replace('_', ' ').title()
                            )
                        else:
                            status_name = volatile_status.replace('_', ' ').title()
                            message = safe_translate(
                                "volatile_status_unknown_apply",
                                pokemon_name=pokemon_name,
                                status_name=status_name
                            )
                        effect_messages.append(message)

                    # Volatile statuses removed
                    removed_volatiles = before - after if before else set()
                    for volatile_status in removed_volatiles:
                        normalized_status = normalize_status_name(volatile_status)
                        translation_key = f"volatile_{normalized_status}_remove"

                        if normalized_status in constants.KNOWN_VOLATILE_STATUSES:
                            message = safe_translate(
                                translation_key,
                                pokemon_name=pokemon_name,
                                status_name=volatile_status.replace('_', ' ').title()
                            )
                        else:
                            status_name = volatile_status.replace('_', ' ').title()
                            message = safe_translate(
                                "volatile_status_unknown_remove",
                                pokemon_name=pokemon_name,
                                status_name=status_name
                            )
                        effect_messages.append(message)

            # Handle HP changes (healing detection)
            elif key.endswith('.hp'):
                target = 'user' if key.startswith('user.') else 'opponent'
                pokemon_name = get_pokemon_name(target)

                # Only show healing messages (HP increased)
                if isinstance(before, (int, float)) and isinstance(after, (int, float)) and after > before:
                    heal_amount = after - before
                    message = safe_translate(
                        "effect_health_restored",
                        pokemon_name=pokemon_name,
                        heal_amount=heal_amount
                    )
                    effect_messages.append(message)

            # Handle stat boost changes
            elif any(key.endswith(f'.{stat}_boost') for stat in ['attack', 'defense', 'special_attack', 'special_defense', 'speed', 'accuracy', 'evasion']):
                target = 'user' if key.startswith('user.') else 'opponent'
                pokemon_name = get_pokemon_name(target)

                # Extract stat name from key
                stat_part = key.split('.')[-1].replace('_boost', '')
                stat_names = {
                    'attack': "Attack", 'defense': "Defense",
                    'special_attack': "Special Attack", 'special_defense': "Special Defense",
                    'speed': "Speed", 'accuracy': "Accuracy", 'evasion': "Evasion"
                }
                stat_name = stat_names.get(stat_part, stat_part.replace('_', ' ').title())

                if isinstance(before, (int, float)) and isinstance(after, (int, float)):
                    change_amount = after - before
                    if change_amount != 0:
                        direction = "increased" if change_amount > 0 else "decreased"
                        message = safe_translate(
                            "effect_stat_change",
                            pokemon_name=pokemon_name,
                            stat=stat_name,
                            direction=direction,
                            amount=abs(change_amount)
                        )
                        effect_messages.append(message)

            # Handle weather changes
            elif key == 'weather':
                if before != after:
                    # Weather started
                    if before is None and after is not None:
                        weather_name = after.replace('-', ' ').title()
                        message = safe_translate("battle_effect_weather_start", weather=weather_name)
                        effect_messages.append(message)
                    # Weather ended
                    elif before is not None and after is None:
                        weather_name = before.replace('-', ' ').title()
                        message = safe_translate("battle_effect_weather_end", weather=weather_name)
                        effect_messages.append(message)
                    # Weather changed
                    elif before is not None and after is not None:
                        old_weather = before.replace('-', ' ').title()
                        new_weather = after.replace('-', ' ').title()
                        message = safe_translate("battle_effect_weather_end", weather=old_weather)
                        effect_messages.append(message)
                        message = safe_translate("battle_effect_weather_start", weather=new_weather)
                        effect_messages.append(message)

            # Handle side condition changes
            elif '.side_conditions.' in key:
                target = 'user' if key.startswith('user.') else 'opponent'
                condition_name = key.split('.')[-1]

                # Side condition started or increased
                if isinstance(before, (int, float)) and isinstance(after, (int, float)) and after > before:
                    message = safe_translate(
                        "battle_effect_side_condition",
                        condition=condition_name.replace('_', ' ').title(),
                        side="your team" if target == 'user' else "the opposing team"
                    )
                    effect_messages.append(message)

            # Handle wish changes
            elif key.endswith('.wish'):
                target = 'user' if key.startswith('user.') else 'opponent'
                pokemon_name = get_pokemon_name(target)

                # Wish started (assuming tuple format: (turns, heal_amount))
                if isinstance(after, tuple) and len(after) >= 2 and after[1] > 0:
                    if not isinstance(before, tuple) or before[1] == 0:
                        heal_amount = after[1]
                        message = safe_translate(
                            "wish_started",
                            pokemon_name=pokemon_name,
                            heal_amount=heal_amount
                        )
                        effect_messages.append(message)

            # Handle future sight changes
            elif key.endswith('.future_sight'):
                target = 'user' if key.startswith('user.') else 'opponent'

                # Future sight started
                if isinstance(after, tuple) and len(after) >= 2 and after[0] > 0:
                    if not isinstance(before, tuple) or before[0] == 0:
                        user_pokemon_name = get_pokemon_name(target)
                        message = safe_translate(
                            "futuresight_start",
                            pokemon_name=user_pokemon_name,
                            target_pokemon="the opposing Pokemon"
                        )
                        effect_messages.append(message)

                # Future sight decremented (still active)
                elif isinstance(before, tuple) and isinstance(after, tuple) and len(before) >= 1 and len(after) >= 1:
                    if before[0] > after[0] and after[0] > 0:
                        message = safe_translate(
                            "futuresight_still_active",
                            side="your team" if target == 'user' else "the opposing team"
                        )
                        effect_messages.append(message)

                # Future sight ended (hit)
                elif isinstance(before, tuple) and isinstance(after, tuple) and len(before) >= 1 and len(after) >= 1:
                    if before[0] > 0 and after[0] == 0:
                        message = safe_translate(
                            "futuresight_hits",
                            side="your team" if target == 'user' else "the opposing team"
                        )
                        effect_messages.append(message)

        except Exception as e:
            print(f"Error processing state change {change}: {e}")
            effect_messages.append(f"Battle effect occurred (processing error)")
            continue

    return effect_messages

def validate_pokemon_status(pokemon):
    """
    Ensure Pokemon has valid battle_status and volatile_status.
    """

    # Valid status codes from const.py
    valid_statuses = {
        "brn", "frz", "par", "psn", "tox", "slp",
        "confusion", "flinching", "fainted", "fighting"
    }

    current_status = getattr(pokemon, 'battle_status', 'fighting')

    # Ensure volatile_status exists
    if not hasattr(pokemon, 'volatile_status'):
        pokemon.volatile_status = set()

    # If status is not valid, default to fighting (or fainted if HP <= 0)
    if current_status not in valid_statuses:
        if hasattr(pokemon, 'hp') and pokemon.hp <= 0:
            return 'fainted'
        else:
            return 'fighting'

    # If Pokemon is fainted but status isn't fainted, override
    if hasattr(pokemon, 'hp') and pokemon.hp <= 0 and current_status != 'fainted':
        return 'fainted'

    return current_status


def process_battle_data(
    battle_info: dict,
    multiplier: float,
    main_pokemon,
    enemy_pokemon,
    user_attack: str,
    enemy_attack: str,
    dmg_from_user_move: int,
    dmg_from_enemy_move: int,
    user_hp_after: int,
    opponent_hp_after: int,
    battle_status: str,
    pokemon_encounter: int,
    translator,
    changes
) -> str:
    """
    Generate complete battle message from battle data.

    This function centralizes all battle message generation and now uses
    format_move_name to display official move names.
    """

    if not isinstance(battle_info, dict):
        return translator.translate("invalid_battle_data_error")

    # Initialize message components
    message_parts = []

    try:
        # 1. Multiplier display
        formatted_multiplier = f"{multiplier:.1f}"
        message_parts.append(
            translator.translate("battle_multiplier_display", multiplier=formatted_multiplier)
        )

        # 2. Enemy attack section
        if enemy_attack is not "splash" or None:

            # --- NEW: Format enemy move name ---
            formatted_enemy_attack = format_move_name(enemy_attack)

            enemy_attack_msg = translator.translate(
                "enemy_attack_announcement",
                pokemon_name=enemy_pokemon.name.capitalize(),
                attack_name=formatted_enemy_attack  # Use the formatted name
            )
            message_parts.append(enemy_attack_msg)

        # 3. User attack section
        if user_attack is not "splash" or None:

            # Handle special battle statuses first
            if battle_status and battle_status != "fighting":
                status_msg = _handle_special_battle_status(
                    main_pokemon, battle_status, translator
                )
                if status_msg:
                    message_parts.append(status_msg)
            else:
                # --- NEW: Format user move name ---
                formatted_user_attack = format_move_name(user_attack)

                # Normal attack resolution
                user_attack_msg = translator.translate(
                    "player_attack_announcement",
                    pokemon_name=main_pokemon.name.capitalize(),
                    attack_name=formatted_user_attack  # Use the formatted name
                )
                message_parts.append(user_attack_msg)

        # 4. Process all other battle effect instructions
        if isinstance(battle_info, dict) and 'instructions' in battle_info:
            try:
                effects_messages = _process_battle_effects(
                    battle_info['instructions'],
                    translator,
                    main_pokemon=main_pokemon,
                    enemy_pokemon=enemy_pokemon,
                    current_state=battle_info.get('state'),
                    changes=changes
                )
                if effects_messages:
                    message_parts.extend(effects_messages)
            except Exception as e:
                message_parts.append(
                    translator.translate("battle_effects_error", error=str(e)[:50])
                )

        # Join all message parts with newlines
        final_message = "\n".join(filter(None, message_parts))

        if not final_message:
            return translator.translate("battle_message_empty_fallback")

        return final_message

    except Exception as e:
        show_warning_with_traceback(
            exception=e,
            message="Critical error generating battle message"
        )
        error_msg = translator.translate("battle_processing_error", error=str(e)[:100])
        return f"{translator.translate('battle_multiplier_display', multiplier=multiplier)}\n{error_msg}"


def _handle_special_battle_status(main_pokemon, battle_status: str, translator) -> str:
    """Handle special battle status conditions using the provided constants."""

    try:

        status_messages = {
            constants.SLEEP: "pokemon_is_sleeping",
            constants.PARALYZED: "pokemon_is_paralyzed",
            constants.FROZEN: "pokemon_is_frozen",
            constants.BURN: "pokemon_is_burned",
            constants.POISON: "pokemon_is_poisoned",
            constants.TOXIC: "pokemon_is_badly_poisoned",
            constants.CONFUSION: "pokemon_is_confused",
            constants.FLINCH: "pokemon_flinched",
            constants.TAUNT: "pokemon_is_taunted"
        }

        # Check if we have a predefined message for this status
        if battle_status in status_messages:
            return translator.translate(
                status_messages[battle_status],
                pokemon_name=main_pokemon.name.capitalize()
            )
        else:
            # Generic status message for unknown conditions
            return translator.translate(
                "pokemon_special_condition",
                pokemon_name=main_pokemon.name.capitalize(),
                condition=battle_status.replace('_', ' ').title()
            )

    except Exception as e:
        # Non‐fatal: return generic message
        show_warning_with_traceback(
            exception=e,
            message="Error handling special battle status"
        )
        return translator.translate(
            "pokemon_special_condition",
            pokemon_name=main_pokemon.name.capitalize(),
            condition=battle_status.replace('_', ' ').title()
        )

def calculate_hp(base_stat_hp, level, ev, iv):
    ev_value = ev["hp"] / 4
    iv_value = iv["hp"]
    #hp = int(((iv + 2 * (base_stat_hp + ev) + 100) * level) / 100 + 10)
    hp = int((((((base_stat_hp + iv_value) * 2 ) + ev_value) * level) / 100) + level + 10)
    return hp