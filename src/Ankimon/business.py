import base64

def special_pokemon_names_for_min_level(name):
    if name == "flabébé":
        return "flabebe"
    elif name == "sirfetch'd":
        return "sirfetchd"
    elif name == "farfetch'd":
        return "farfetchd"
    elif name == "porygon-z":
        return "porygonz"
    elif name == "kommo-o":
        return "kommoo"
    elif name == "hakamo-o":
        return "hakamoo"
    elif name == "jangmo-o":
        return "jangmoo"
    elif name == "mr. rime":
        return "mrrime"
    elif name == "mr. mime":
        return "mrmime"
    elif name == "mime jr.":
        return "mimejr"
    elif name == "nidoran♂":
        return "nidoranm"
    elif name == "nidoran":
        return "nidoranf"
    elif name == "keldeo[e]":
        return "keldeo"
    elif name == "mew[e]":
        return "mew"
    elif name == "deoxys[e]":
        return "deoxys"
    elif name == "jirachi[e]":
        return "jirachi"
    elif name == "arceus[e]":
        return "arceus"
    elif name == "shaymin[e]":
        return "shaymin-land"
    elif name == "darkrai [e]":
        return "darkrai"
    elif name == "manaphy[e]":
        return "manaphy"
    elif name == "phione[e]":
        return "phione"
    elif name == "celebi[e]":
        return "celebi"
    elif name == "magearna[e]":
        return "magearna"
    elif name == "type: null":
        return "typenull"
    else:
        #showWarning("Error in Handling Pokémon name")
        return name
    
def get_image_as_base64(path):
    with open(path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def split_string_by_length(input_string, max_length):
    current_length = 0
    current_line = []

    for word in input_string.split():
        word_length = len(word)  # Change this to calculate length in pixels

        if current_length + len(current_line) + word_length <= max_length:
            current_line.append(word)
            current_length += word_length
        else:
            yield ' '.join(current_line)
            current_line = [word]
            current_length = word_length

    yield ' '.join(current_line)

def split_japanese_string_by_length(input_string, max_length):
    max_length = 30
    current_length = 0
    current_line = ""

    for char in input_string:
        if current_length + 1 <= max_length:
            current_line += char
            current_length += 1
        else:
            yield current_line
            current_line = char
            current_length = 1

    if current_line:  # Ensure the last line is also yielded
        yield current_line

def resize_pixmap_img(pixmap, max_width):
    original_width = pixmap.width()
    original_height = pixmap.height()
    new_width = max_width
    new_height = (original_height * max_width) // original_width
    pixmap2 = pixmap.scaled(new_width, new_height)
    return pixmap2

def calc_experience(base_experience, enemy_level):
    exp = base_experience * enemy_level / 7
    return exp