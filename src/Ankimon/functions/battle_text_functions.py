def effectiveness_text(effect_value):
    if effect_value == 0:
        effective_txt = "has missed."
    elif effect_value <= 0.5:
        effective_txt = "was not very effective."
    elif effect_value <= 1:
        effective_txt = "was effective."
    elif effect_value <= 1.5:
        effective_txt = "was very effective !"
    elif effect_value <= 2:
        effective_txt = "was super effective !"
    else:
        effective_txt = "was effective."
        #return None
    return effective_txt