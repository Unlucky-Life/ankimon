These settings do not sync and require a restart to apply.

- `Cards per Round` [number]: Number of Cards until next Attackround

Possible Generation are:
If you want to play with Pokemon from a certain generation, set them as True
- `Generation1` [True/False]
- `Generation2` [True/False]
- `Generation3` [True/False]
- `Generation4` [True/False]
- `Generation5` [True/False]
- `Generation6` [True/False]
- `Generation7` [True/False]
- `Generation8` [True/False]
- `Generation9` [True/False]

Pokemon Gif Animations:
You can decide if you want the Gif Animations in the anki reviewer
- `reviewer_image_gif` [True/False]

Ankimon Window Key:
You can decide which letter key should be pressed additionally to controll / command (like M etc) to open and close the ankimon window from the anki reviewer
- `key_for_opening_closing_ankimon` [A - Z]

Main Pokemon in Reviewer:
If `show_mainpkmn_in_reviewer` is set to 0, you will only see the wild Pokémon when reviewing cards. Setting it to 1 will display both your main Pokémon and the wild Pokémon in the reviewer, with the HP bar on the same height. If set to 2, you'll have a more "battle" look between your main Pokémon and the wild Pokémon.
- `show_mainpkmn_in_reviewer` [0/1/2]

Reviewer Text Message Box:
Decide if you would like to see the colorful popup messages in the anki reviewer
- `reviewer_text_message_box` [True/False]

`reviewer_text_message_box_time` allows you to set the duration, in seconds, for which the pop-up message will be displayed in the reviewer.
- `reviewer_text_message_box_time` [1,2,3,4,5] (time in seconds)

Reviewer Pop Up Messages:
Decide if you would like to see the anki popup messages in the anki reviewer when your pokemon levels up or when a wild pokemon is defeated
- `pop_up_dialog_message_on_defeat` [True/False]

Sounds:
You can decide if you want Pokemon Battle Cries in the anki reviewer once a pokemon appears.
- `sounds` [True/False]

In Game Battle Sounds:
You can decide if you want Pokemon Battle Cries to be replayed every 10 cards.
- `battle_sounds` [True/False]

To enable sound effects such as healing your main Pokémon, hurting your Pokémon, or affecting enemy Pokémon, set `sound_effects` to `true`. If set to `false`, no sound effects will be activated.
- `sound_effects` [True/False]

Set `view_main_front` to `true` to view your main Pokémon from the front in the reviewer when `reviewer_image_gif` is also set to `true`. If `view_main_front` is set to `false`, you will see your main Pokémon's GIF from the back in the reviewer.
- `view_main_front` [True/False]

Set `ssh` to `true` if you encounter issues opening Ankimon due to internet restrictions like Eduroam. Set it to `false` to potentially resolve these issues.
- `ssh` [True/False]

Set `animate_time` to `true` to enable a small animation in the reviewer. This animation is displayed when you or the wild Pokémon is taking damage. `false` disables this.
- `animate_time` [True/False]

Set `gif_in_collection` to `true` to view GIF images instead of sprites of your caught Pokémon in your collection.
- `gif_in_collection` [True/False]

Setting `hp_bar_config` to `false` removes the HP bar in the reviewer interface.
- `hp_bar_config` [True/False]

Setting `xp_bar_location` to 1 places the XP bar at the top of your screen in the reviewer. If set to 2, the XP bar will appear at the bottom of your screen.
- `xp_bar_location` [1/2]

Setting `xp_bar_config` to `true` will display the XP bar in the reviewer. It will show your main Pokémon's current XP and the amount needed for the next level.
- `xp_bar_config` [True/False]

Setting `YouShallNotPass_Ankimon_News` to `true` deactivates the update patch notes pop-up on Anki startup.
- `YouShallNotPass_Ankimon_News` [True/False]

Setting `automate_battle` to `0` deactivates the automatic defeat or catch in the reviewer. Pokemon will stay alive until you decide to choose to defeat or catch them in the Ankimon Window.
- `automate_battle` [0/1/2]
    - If set to `1`, the wild Pokemon will be automatically caught if it has no more HP.
    - If set to `2`, the wild Pokemon will be defeated if its HP reaches 0, and your main Pokemon will gain experience.

Setting `catch_key` to a letter allows you to catch pokemons inside of the reviewer when their hp reaches 0 by pressing control and your letter - default is D.
- `catch_key` [A - Z]

Setting `defeat_key` to a letter allows you to defeat pokemons inside of the reviewer when their hp reaches 0 by pressing control and your letter - default is F.
- `defeat_key` [A - Z]

`review_hp_bar_thickness` sets the pixel thickness of the HP bar in the reviewer. 
- Setting it to `2` will result in an 8px thickness.
- Setting it to `3` will result in a 12px thickness.
- Setting it to `4` will result in a 16px thickness.
- Setting it to `5` will result in a 20px thickness.

Language Options (Select a Number from the ones below to the corresponding language you would like to read your pokemon names and descriptions):

    | ID  | Language               | Official |

    | 1   | Japanese (Hir & Kata ) | Yes      |

    | 2   | Japanese (Roomaji)     | Yes      |

    | 3   | Korean                 | Yes      |

    | 4   | Chinese (Traditional)  | Yes      |

    | 5   | French                 | Yes      |

    | 6   | German                 | Yes      |

    | 7   | Spanish                | Yes      |

    | 8   | Italian                | Yes      |

    | 9   | English                | Yes      |

    | 10  | Czech                  | No       |

    | 11  | Japanese               | Yes      |

    | 12  | Chinese (Simplified)   | Yes      |

    | 13  | Portuguese (Brazil)    | No       |
