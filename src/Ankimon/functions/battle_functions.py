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


def _process_battle_effects(instructions: list, translator=None) -> list:
    """
    Process battle instructions including volatile status effects using constants.
    Enhanced with debugging and fallback message generation.
    """
    
    if not instructions or not isinstance(instructions, list):
        return []
        
    effect_messages = []
    
    for i, instr in enumerate(instructions):
        if not instr or not isinstance(instr, (list, tuple)) or len(instr) < 2:
            continue
            
        try:
            action = instr[0]
            target_side = instr[1] if len(instr) > 1 else None
            
            # Handle regular status application
            if action == constants.MUTATOR_APPLY_STATUS and len(instr) >= 3:
                status = instr[2]
                pokemon_side = ("Your Pokemon" if target_side == 'user' else "Enemy Pokemon")
                
                status_names = {
                    constants.SLEEP: "sleep",
                    constants.PARALYZED: "paralysis", 
                    constants.FROZEN: "freeze",
                    constants.BURN: "burn",
                    constants.POISON: "poison",
                    constants.TOXIC: "toxic poisoning"
                }
                
                status_name = status_names.get(status, status.replace('_', ' '))
                
                # Try translator first, fallback to direct message
                try:
                    if translator:
                        message = translator.translate(
                            "effect_status_applied",
                            pokemon_side=pokemon_side,
                            status=status_name.title()
                        )
                    else:
                        message = f"{pokemon_side} was afflicted with {status_name}!"
                except:
                    message = f"{pokemon_side} was afflicted with {status_name}!"
                
                effect_messages.append(message)
            
            # Handle volatile status application - FIXED SYNTAX
            elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS and len(instr) >= 3:
                volatile_status = instr[2]
                pokemon_side = ("Your Pokemon" if target_side == 'user' else "Enemy Pokemon")
                
                # Map volatile status to readable names
                volatile_status_names = {
                    'roost': "temporarily loses its Flying type",
                    'substitute': "created a substitute",
                    'confusion': "became confused",
                    'taunt': "was taunted",
                    'encore': "was encored",
                    'disable': "was disabled",
                    'torment': "was tormented",
                    'magnet_rise': "rose into the air with electromagnetic force",
                    'telekinesis': "was lifted by telekinesis"
                }
                
                status_description = volatile_status_names.get(volatile_status, f"was affected by {volatile_status.replace('_', ' ')}")
                
                # Try translator first, fallback to direct message
                try:
                    if translator:
                        message = translator.translate(
                            "effect_volatile_status_applied",
                            pokemon_side=pokemon_side,
                            status=status_description
                        )
                    else:
                        message = f"{pokemon_side} {status_description}!"
                except:
                    message = f"{pokemon_side} {status_description}!"
                
                effect_messages.append(message)
            
            # Handle volatile status removal - FIXED SYNTAX
            elif action == constants.MUTATOR_REMOVE_VOLATILE_STATUS and len(instr) >= 3:
                volatile_status = instr[2]
                pokemon_side = ("Your Pokemon" if target_side == 'user' else "Enemy Pokemon")
                
                # Special messages for volatile status removal
                volatile_removal_messages = {
                    'roost': "Flying type is restored",
                    'substitute': "substitute faded",
                    'confusion': "snapped out of confusion",
                    'taunt': "taunt wore off",
                    'encore': "encore ended",
                    'disable': "disable wore off",
                    'torment': "torment ended",
                    'magnet_rise': "magnetic force wore off and it fell down",
                    'telekinesis': "telekinesis wore off"
                }
                
                status_description = volatile_removal_messages.get(volatile_status, f"{volatile_status.replace('_', ' ')} wore off")
                
                # Try translator first, fallback to direct message
                try:
                    if translator:
                        message = translator.translate(
                            "effect_volatile_status_removed",
                            pokemon_side=pokemon_side,
                            status=status_description
                        )
                    else:
                        message = f"{pokemon_side}'s {status_description}!"
                except:
                    message = f"{pokemon_side}'s {status_description}!"
                
                effect_messages.append(message)
            
            # Handle stat boosts
            elif action == constants.MUTATOR_BOOST and len(instr) >= 4:
                stat = instr[2]
                amount = instr[3]
                pokemon_side = ("Your Pokemon" if target_side == 'user' else "Enemy Pokemon")
                
                stat_names = {
                    constants.ATTACK: "Attack",
                    constants.DEFENSE: "Defense", 
                    constants.SPECIAL_ATTACK: "Special Attack",
                    constants.SPECIAL_DEFENSE: "Special Defense",
                    constants.SPEED: "Speed",
                    constants.ACCURACY: "Accuracy",
                    constants.EVASION: "Evasion"
                }
                
                stat_name = stat_names.get(stat, stat.replace('-', ' ').title())
                direction = "increased" if amount > 0 else "decreased"
                
                # Try translator first, fallback to direct message
                try:
                    if translator:
                        message = translator.translate(
                            "effect_stat_change",
                            pokemon_side=pokemon_side,
                            stat=stat_name,
                            direction=direction,
                            amount=abs(amount)
                        )
                    else:
                        message = f"{pokemon_side}'s {stat_name} {direction} by {abs(amount)}!"
                except:
                    message = f"{pokemon_side}'s {stat_name} {direction} by {abs(amount)}!"
                
                effect_messages.append(message)
            
            # Handle weather effects
            elif action == constants.MUTATOR_WEATHER_START and len(instr) >= 2:
                weather = instr[1]
                
                # Try translator first, fallback to direct message
                try:
                    if translator:
                        message = translator.translate(
                            "battle_effect_weather_start",
                            weather=weather.replace('-', ' ').title()
                        )
                    else:
                        message = f"{weather.replace('-', ' ').title()} weather started!"
                except:
                    message = f"{weather.replace('-', ' ').title()} weather started!"
                
                effect_messages.append(message)
                
            elif action == constants.MUTATOR_WEATHER_END and len(instr) >= 2:
                weather = instr[1]
                
                # Try translator first, fallback to direct message
                try:
                    if translator:
                        message = translator.translate(
                            "battle_effect_weather_end",
                            weather=weather.replace('-', ' ').title()
                        )
                    else:
                        message = f"{weather.replace('-', ' ').title()} weather ended!"
                except:
                    message = f"{weather.replace('-', ' ').title()} weather ended!"
                
                effect_messages.append(message)
                
        except Exception as e:
            # Log error but continue processing
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
                
        
        # 4. Process detailed battle effects from battle_info
        if isinstance(battle_info, dict) and 'instructions' in battle_info:
            try:
                effects_messages = _process_battle_effects(
                    battle_info['instructions'], translator
                )
                if effects_messages:
                    message_parts.extend(effects_messages)
            except Exception as e:
                # Continue processing even if effects parsing fails
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