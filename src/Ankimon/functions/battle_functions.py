import copy
from ..poke_engine import constants
from ..pyobj.error_handler import show_warning_with_traceback

def update_pokemon_battle_status(battle_info: dict, enemy_pokemon, main_pokemon):
    """
    Update Pokemon battle status based on battle instructions.
    
    Processes battle instructions to track status effects for both Pokemon.
    Status effects persist until explicitly removed by 'remove_status' instruction.
    """
    
    if not isinstance(battle_info, dict) or 'instructions' not in battle_info:
        return False, False
    
    instructions = battle_info.get('instructions', [])
    if not instructions or not isinstance(instructions, list):
        return False, False
    
    enemy_status_changed = False
    main_status_changed = False
    
    try:
        # Process each instruction in the battle
        for instr in instructions:
            if not instr or not isinstance(instr, (list, tuple)) or len(instr) < 3:
                continue
                
            action = instr[0]
            target = instr[1] 
            status_value = instr[2]
            
            # Handle status application
            if action == constants.MUTATOR_APPLY_STATUS:
                if target == 'opponent':
                    # Update enemy Pokemon status
                    old_status = getattr(enemy_pokemon, 'battle_status', 'fighting')
                    enemy_pokemon.battle_status = status_value
                    if old_status != status_value:
                        enemy_status_changed = True
                        
                elif target == 'user':
                    # Update main Pokemon status  
                    old_status = getattr(main_pokemon, 'battle_status', 'fighting')
                    main_pokemon.battle_status = status_value
                    if old_status != status_value:
                        main_status_changed = True
            
            # Handle status removal
            elif action == constants.MUTATOR_REMOVE_STATUS:
                if target == 'opponent':
                    # Remove enemy Pokemon status - return to fighting
                    old_status = getattr(enemy_pokemon, 'battle_status', 'fighting')
                    enemy_pokemon.battle_status = 'fighting'
                    if old_status != 'fighting':
                        enemy_status_changed = True
                        
                elif target == 'user':
                    # Remove main Pokemon status - return to fighting
                    old_status = getattr(main_pokemon, 'battle_status', 'fighting')  
                    main_pokemon.battle_status = 'fighting'
                    if old_status != 'fighting':
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
        return False, False


def validate_pokemon_status(pokemon):
    """
    Ensure Pokemon has a valid battle_status that matches status_colors_html keys.
    """
    
    # Valid status codes from const.py
    valid_statuses = {
        "brn", "frz", "par", "psn", "tox", "slp", 
        "confusion", "flinching", "fainted", "fighting"
    }
    
    current_status = getattr(pokemon, 'battle_status', 'fighting')
    
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


def _process_battle_effects(instructions: list, translator) -> list:
    """Process battle instructions using the constants for proper effect handling."""
    
    if not instructions or not isinstance(instructions, list):
        return []
        
    effect_messages = []
    
    for instr in instructions:
        if not instr or not isinstance(instr, (list, tuple)) or len(instr) < 2:
            continue
            
        try:
            action = instr[0]
            target_side = instr[1] if len(instr) > 1 else None
            
            if action == constants.MUTATOR_APPLY_STATUS and len(instr) >= 3:
                status = instr[2]
                pokemon_side = (translator.translate("your_pokemon") 
                              if target_side == 'user' 
                              else translator.translate("enemy_pokemon"))
                
                # Map status constants to readable names
                status_names = {
                    constants.SLEEP: "sleep",
                    constants.PARALYZED: "paralysis", 
                    constants.FROZEN: "freeze",
                    constants.BURN: "burn",
                    constants.POISON: "poison",
                    constants.TOXIC: "toxic poisoning"
                }
                
                status_name = status_names.get(status, status.replace('_', ' '))
                effect_messages.append(
                    translator.translate(
                        "effect_status_applied",
                        pokemon_side=pokemon_side,
                        status=status_name.title()
                    )
                )
            
            elif action == constants.MUTATOR_BOOST and len(instr) >= 4:
                stat = instr[2]
                amount = instr[3]
                pokemon_side = (translator.translate("your_pokemon") 
                              if target_side == 'user' 
                              else translator.translate("enemy_pokemon"))
                
                # Map stat constants to readable names
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
                
                effect_messages.append(
                    translator.translate(
                        "effect_stat_change",
                        pokemon_side=pokemon_side,
                        stat=stat_name,
                        direction=translator.translate(f"stat_{direction}"),
                        amount=abs(amount)
                    )
                )
            
            elif action == constants.MUTATOR_WEATHER_START and len(instr) >= 2:
                weather = instr[1]
                effect_messages.append(
                    translator.translate(
                        "battle_effect_weather_start",
                        weather=weather.replace('-', ' ').title()
                    )
                )
            elif action == constants.MUTATOR_WEATHER_END and len(instr) >= 2:
                weather = instr[1]
                effect_messages.append(
                    translator.translate(
                        "battle_effect_weather_end",
                        weather=weather.replace('-', ' ').title()
                    )
                )
        except Exception as e:
            # Non‐fatal: report and continue
            show_warning_with_traceback(
                exception=e,
                message="Error processing battle effects"
            )
    
    return effect_messages

def calculate_hp(base_stat_hp, level, ev, iv):
    ev_value = ev["hp"] / 4
    iv_value = iv["hp"]
    #hp = int(((iv + 2 * (base_stat_hp + ev) + 100) * level) / 100 + 10)
    hp = int((((((base_stat_hp + iv_value) * 2 ) + ev_value) * level) / 100) + level + 10)
    return hp