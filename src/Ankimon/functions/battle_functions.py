import copy
from ..poke_engine import constants
from ..pyobj.error_handler import show_warning_with_traceback

def update_pokemon_battle_status(battle_info: dict, enemy_pokemon, main_pokemon):
    """
    Update Pokemon battle status and volatile status based on battle instructions.
    
    Enhanced to handle both regular status and volatile status effects.
    Volatile status effects are temporary and can stack, unlike regular status.
    """
    
    if not isinstance(battle_info, dict) or 'instructions' not in battle_info:
        return False, False
    
    instructions = battle_info.get('instructions', [])
    if not instructions or not isinstance(instructions, list):
        return False, False
    
    enemy_status_changed = False
    main_status_changed = False
    
    try:
        # Initialize volatile_status if not present
        if not hasattr(enemy_pokemon, 'volatile_status'):
            enemy_pokemon.volatile_status = set()
        if not hasattr(main_pokemon, 'volatile_status'):
            main_pokemon.volatile_status = set()
            
        # Process each instruction in the battle
        for instr in instructions:
            if not instr or not isinstance(instr, (list, tuple)) or len(instr) < 3:
                continue
                
            action = instr[0]
            target = instr[1] 
            status_value = instr[2]
            
            # Handle regular status application
            if action == constants.MUTATOR_APPLY_STATUS:
                if target == 'opponent':
                    old_status = getattr(enemy_pokemon, 'battle_status', 'fighting')
                    enemy_pokemon.battle_status = status_value
                    if old_status != status_value:
                        enemy_status_changed = True
                elif target == 'user':
                    old_status = getattr(main_pokemon, 'battle_status', 'fighting')
                    main_pokemon.battle_status = status_value
                    if old_status != status_value:
                        main_status_changed = True
            
            # Handle regular status removal
            elif action == constants.MUTATOR_REMOVE_STATUS:
                if target == 'opponent':
                    old_status = getattr(enemy_pokemon, 'battle_status', 'fighting')
                    enemy_pokemon.battle_status = 'fighting'
                    if old_status != 'fighting':
                        enemy_status_changed = True
                elif target == 'user':
                    old_status = getattr(main_pokemon, 'battle_status', 'fighting')  
                    main_pokemon.battle_status = 'fighting'
                    if old_status != 'fighting':
                        main_status_changed = True
            
            # Handle volatile status application - NEW
            elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS:
                if target == 'opponent':
                    old_volatile = enemy_pokemon.volatile_status.copy()
                    enemy_pokemon.volatile_status.add(status_value)
                    if old_volatile != enemy_pokemon.volatile_status:
                        enemy_status_changed = True
                elif target == 'user':
                    old_volatile = main_pokemon.volatile_status.copy()
                    main_pokemon.volatile_status.add(status_value)
                    if old_volatile != main_pokemon.volatile_status:
                        main_status_changed = True
            
            # Handle volatile status removal - NEW
            elif action == constants.MUTATOR_REMOVE_VOLATILE_STATUS:
                if target == 'opponent':
                    old_volatile = enemy_pokemon.volatile_status.copy()
                    enemy_pokemon.volatile_status.discard(status_value)
                    if old_volatile != enemy_pokemon.volatile_status:
                        enemy_status_changed = True
                elif target == 'user':
                    old_volatile = main_pokemon.volatile_status.copy()
                    main_pokemon.volatile_status.discard(status_value)
                    if old_volatile != main_pokemon.volatile_status:
                        main_status_changed = True
                        
                # Handle Future Sight instructions - NEW
                elif action == constants.MUTATOR_FUTURESIGHT_START and len(instr) >= 4:
                    # ['futuresight_start', 'user', 'cresselia', 0]
                    # Format: [action, side, pokemon_name, initial_counter]
                    side = instr[1]
                    pokemon_name = instr[2] 
                    counter = instr[3]
                    
                    # Future Sight affects the opposing side, so track on opposite side
                    if side == 'user':
                        # User's Future Sight will hit opponent in 2 turns
                        enemy_status_changed = True
                    else:
                        # Opponent's Future Sight will hit user in 2 turns  
                        main_status_changed = True
                        
                elif action == constants.MUTATOR_FUTURESIGHT_DECREMENT:
                    # ['futuresight_decrement', 'user']
                    # Just decrement the counter - the engine handles this
                    if instr[1] == 'user':
                        main_status_changed = True
                    else:
                        enemy_status_changed = True
        
        # Handle fainted status based on HP
        if hasattr(enemy_pokemon, 'hp') and enemy_pokemon.hp <= 0:
            old_status = getattr(enemy_pokemon, 'battle_status', 'fighting')
            enemy_pokemon.battle_status = 'fainted'
            if old_status != 'fainted':
                enemy_status_changed = True
                
        if hasattr(main_pokemon, 'hp') and main_pokemon.hp <= 0:
            old_status = getattr(main_pokemon, 'battle_status', 'fighting')
            main_pokemon.battle_status = 'fainted' 
            if old_status != 'fainted':
                main_status_changed = True
        
        return enemy_status_changed, main_status_changed
        
    except Exception as e:
        # If there's an error, ensure Pokemon have valid status
        if not hasattr(enemy_pokemon, 'battle_status'):
            enemy_pokemon.battle_status = 'fighting'
        if not hasattr(main_pokemon, 'battle_status'):
            main_pokemon.battle_status = 'fighting'
        if not hasattr(enemy_pokemon, 'volatile_status'):
            enemy_pokemon.volatile_status = set()
        if not hasattr(main_pokemon, 'volatile_status'):
            main_pokemon.volatile_status = set()
        return False, False


def _process_battle_effects(
    instructions: list,
    translator,
    main_pokemon=None,
    enemy_pokemon=None,
    current_state=None
) -> list:
    """
    Process all battle instructions with Pokemon names and persistent effect messages.
    This version will NOT show 'still' messages for fainted Pokemon or for any
    status/volatile that is first applied this turn.
    """
    if not instructions or not isinstance(instructions, list):
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

    # Track which statuses/volatiles are newly applied this turn
    newly_applied_statuses = set()
    newly_applied_volatiles = set()
    if instructions:
        for instr in instructions:
            if not instr or not isinstance(instr, (list, tuple)) or len(instr) < 3:
                continue
            action, target, value = instr[0], instr[1], instr[2]
            if action == constants.MUTATOR_APPLY_STATUS:
                newly_applied_statuses.add((target, normalize_status_name(value)))
            elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS:
                newly_applied_volatiles.add((target, normalize_status_name(value)))

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

    # Prepend persistent effect messages to the main list
    if current_state and (main_pokemon or enemy_pokemon):
        effect_messages.extend(check_persistent_effects())

    # Process instructions for apply/remove messages
    for instr in instructions:
        if not instr or not isinstance(instr, (list, tuple)) or len(instr) < 2:
            continue

        try:
            action = instr[0]
            target_side = instr[1] if len(instr) > 1 else None

            # Handle regular status application
            if action == constants.MUTATOR_APPLY_STATUS and len(instr) >= 3:
                status = instr[2]
                pokemon_name = get_pokemon_name(target_side)
                normalized_status = normalize_status_name(status)
                translation_key = f"status_{normalized_status}_apply"

                if status.lower() in constants.KNOWN_REGULAR_STATUSES:
                    message = safe_translate(
                        translation_key,
                        pokemon_name=pokemon_name,
                        status_name=status.replace('_', ' ').title()
                    )
                else:
                    status_name = status.replace('_', ' ').title()
                    message = safe_translate(
                        "status_unknown_apply",
                        pokemon_name=pokemon_name,
                        status_name=status_name
                    )
                effect_messages.append(message)

            # Handle regular status removal
            elif action == constants.MUTATOR_REMOVE_STATUS and len(instr) >= 3:
                status = instr[2]
                pokemon_name = get_pokemon_name(target_side)
                normalized_status = normalize_status_name(status)
                translation_key = f"status_{normalized_status}_remove"

                if status.lower() in constants.KNOWN_REGULAR_STATUSES:
                    message = safe_translate(
                        translation_key,
                        pokemon_name=pokemon_name,
                        status_name=status.replace('_', ' ').title()
                    )
                else:
                    status_name = status.replace('_', ' ').title()
                    message = safe_translate(
                        "status_unknown_remove",
                        pokemon_name=pokemon_name,
                        status_name=status_name
                    )
                effect_messages.append(message)

            # Handle volatile status application
            elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS and len(instr) >= 3:
                volatile_status = instr[2]
                pokemon_name = get_pokemon_name(target_side)
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

            # Handle volatile status removal
            elif action == constants.MUTATOR_REMOVE_VOLATILE_STATUS and len(instr) >= 3:
                volatile_status = instr[2]
                pokemon_name = get_pokemon_name(target_side)
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
                
            elif action == constants.MUTATOR_HEAL and len(instr) >= 3:
                # ['heal', 'user' | 'opponent', amount]
                heal_amount = instr[2]                     # numeric HP restored
                pokemon_name = get_pokemon_name(target_side)

                # translator key:  "effect_health_restored"
                # placeholders:    {pokemon_name}, {heal_amount}
                message = safe_translate(
                    "effect_health_restored",
                    pokemon_name=pokemon_name,
                    heal_amount=heal_amount
                )
                effect_messages.append(message)
            
            # Handle stat boosts
            elif action == constants.MUTATOR_BOOST and len(instr) >= 4:
                stat, amount = instr[2], instr[3]
                pokemon_name = get_pokemon_name(target_side)
                stat_names = {
                    constants.ATTACK: "Attack", constants.DEFENSE: "Defense",
                    constants.SPECIAL_ATTACK: "Special Attack", constants.SPECIAL_DEFENSE: "Special Defense",
                    constants.SPEED: "Speed", constants.ACCURACY: "Accuracy", constants.EVASION: "Evasion"
                }
                stat_name = stat_names.get(stat, stat.replace('-', ' ').title())
                direction = "increased" if amount > 0 else "decreased"
                message = safe_translate(
                    "effect_stat_change", pokemon_name=pokemon_name, stat=stat_name,
                    direction=direction, amount=abs(amount)
                )
                effect_messages.append(message)

            # Handle weather effects
            elif action == constants.MUTATOR_WEATHER_START and len(instr) >= 2:
                weather = instr[1]
                message = safe_translate("battle_effect_weather_start", weather=weather.replace('-', ' ').title())
                effect_messages.append(message)

            elif action == constants.MUTATOR_WEATHER_END and len(instr) >= 2:
                weather = instr[1]
                message = safe_translate("battle_effect_weather_end", weather=weather.replace('-', ' ').title())
                effect_messages.append(message)
                
            # Handle Future Sight effects
            elif action == constants.MUTATOR_FUTURESIGHT_START and len(instr) >= 4:
                # ['futuresight_start', 'user', 'cresselia', 0]
                side = instr[1]
                pokemon_name = instr[2]
                counter = instr[3]
                
                user_pokemon_name = get_pokemon_name(side)
                message = safe_translate(
                    "futuresight_start",
                    pokemon_name=user_pokemon_name,
                    target_pokemon=pokemon_name
                )
                effect_messages.append(message)
                
            elif action == constants.MUTATOR_FUTURESIGHT_DECREMENT and len(instr) >= 2:
                # ['futuresight_decrement', 'user'] 
                side = instr[1]
                message = safe_translate(
                    "futuresight_still_active",
                    side="your team" if side == 'user' else "the opposing team"
                )
                effect_messages.append(message)
                
            elif action == constants.MUTATOR_FUTURESIGHT_END and len(instr) >= 2:
                # When Future Sight actually deals damage
                side = instr[1]
                message = safe_translate(
                    "futuresight_hits",
                    side="your team" if side == 'user' else "the opposing team"
                )
                effect_messages.append(message)


        except Exception as e:
            print(f"Error processing battle instruction {instr}: {e}")
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
    dmg_in_reviewer: bool,
    translator
) -> str:
    """
    Generate complete battle message from battle data.
    
    This function centralizes all battle message generation, handling:
    - Multiplier display
    - Attack announcements with effectiveness on same line
    - Status conditions and special effects
    - Battle outcome messages without HP display
    - Error handling for edge cases
    """
    
    if not isinstance(battle_info, dict):
        return translator.translate("invalid_battle_data_error")
    
    # Initialize message components
    message_parts = []
    
    try:
        # 1. Multiplier display (always shown first)
        message_parts.append(
            translator.translate("battle_multiplier_display", multiplier=multiplier)
        )
        
        # 2. Enemy attack section (when applicable)
        if (pokemon_encounter > 0 and enemy_pokemon.hp > 0 and 
            dmg_in_reviewer and multiplier < 1):
            
            # Build enemy attack message with effectiveness on same line
            enemy_attack_msg = translator.translate(
                "enemy_attack_announcement",
                pokemon_name=enemy_pokemon.name.capitalize(),
                attack_name=enemy_attack.capitalize()
            )
            
            # Add effectiveness message to same line if applicable
            if dmg_from_enemy_move > 0:
                # Attack was effective - show damage
                damage_msg = translator.translate(
                    "damage_dealt_short",
                    damage=dmg_from_enemy_move,
                    pokemon_name=main_pokemon.name.capitalize()
                )
                enemy_attack_msg += " " + damage_msg
            
            message_parts.append(enemy_attack_msg)
        
        # 3. User attack section (when pokemon encounter is active)
        if pokemon_encounter > 0 and main_pokemon.hp > 0:
            
            # Handle special battle statuses first
            if battle_status and battle_status != "fighting":
                status_msg = _handle_special_battle_status(
                    main_pokemon, battle_status, translator
                )
                if status_msg:
                    message_parts.append(status_msg)
            else:
                # Normal attack resolution
                user_attack_msg = translator.translate(
                    "player_attack_announcement",
                    pokemon_name=main_pokemon.name.capitalize(),
                    attack_name=user_attack.capitalize()
                )
                
                # Add effectiveness message to same line
                if dmg_from_user_move > 0:

                    # Attack was effective - show damage
                    damage_msg = translator.translate(
                        "damage_dealt_short",
                        damage=dmg_from_user_move,
                        pokemon_name=enemy_pokemon.name.capitalize()
                    )
                    user_attack_msg += " " + damage_msg
                
                message_parts.append(user_attack_msg)
                
        
        # In process_battle_data function, find this section:
        if isinstance(battle_info, dict) and 'instructions' in battle_info:
            try:
                effects_messages = _process_battle_effects(
                    battle_info['instructions'], 
                    translator,
                    main_pokemon=main_pokemon,      # NEW - pass Pokemon objects
                    enemy_pokemon=enemy_pokemon,    # NEW - pass Pokemon objects  
                    current_state=battle_info.get('state') # NEW - pass state if available
                )
                if effects_messages:
                    message_parts.extend(effects_messages)
            except Exception as e:
                message_parts.append(
                    translator.translate("battle_effects_error", error=str(e)[:50])
                )
        
        # Join all message parts with newlines (NO HP STATUS SECTION)
        final_message = "\n".join(filter(None, message_parts))
        
        # Ensure we always return something meaningful
        if not final_message.strip():
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