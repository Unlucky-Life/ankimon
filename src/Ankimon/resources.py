from pathlib import Path
import os
import json

addon_dir = Path(__file__).parents[0]

#safe route for updates
user_path = addon_dir / "user_files"
user_path_data = addon_dir / "user_files" / "data_files"
user_path_sprites = addon_dir / "user_files" / "sprites"
user_path_credentials = addon_dir / "user_files" / "data.json"
manifest_path = addon_dir / "manifest.json"

font_path = addon_dir / "addon_files"

# Assign Pokemon Image folder directory name
pkmnimgfolder = addon_dir / "user_files" / "sprites"
backdefault = addon_dir / "user_files" / "sprites" / "back_default"
frontdefault = addon_dir / "user_files" / "sprites" / "front_default"
#Assign saved Pokemon Directory
mypokemon_path = addon_dir / "user_files" / "mypokemon.json"
mainpokemon_path = addon_dir / "user_files" / "mainpokemon.json"
battlescene_path = addon_dir / "addon_sprites" / "battle_scenes"
trainer_sprites_path = addon_dir / "addon_sprites" / "trainers"
battlescene_path_without_dialog = addon_dir / "addon_sprites" / "battle_scenes_without_dialog"
battle_ui_path = addon_dir / "pkmnbattlescene - UI_transp"
type_style_file = addon_dir / "addon_files" / "types.json"
next_lvl_file_path = addon_dir / "addon_files" / "ExpPokemonAddon.csv"
berries_path = addon_dir / "user_files" / "sprites" / "berries"
background_dialog_image_path  = addon_dir / "background_dialog_image.png"
pokedex_image_path = addon_dir / "addon_sprites" / "pokedex_template.jpg"
evolve_image_path = addon_dir / "addon_sprites" / "evo_temp.jpg"
learnset_path = addon_dir / "user_files" / "data_files" / "learnsets.json"
pokedex_path = addon_dir / "user_files" / "data_files" / "pokedex.json"
pokemon_names_file_path = addon_dir / "user_files" / "data_files" / "pokemon_names.json"
moves_file_path = addon_dir / "user_files" / "data_files" / "moves.json"
move_names_file_path = addon_dir / "user_files" / "data_files" / "move_names.json"
items_path = addon_dir / "user_files" / "sprites" / "items"
badges_path = addon_dir / "user_files" / "sprites" / "badges"
itembag_path = addon_dir / "user_files" / "items.json"
badgebag_path = addon_dir / "user_files" / "badges.json"
pokenames_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_names.csv"
pokedesc_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_flavor_text.csv"
poke_evo_path = addon_dir / "user_files" / "data_files" / "pokemon_evolution.csv"
poke_species_path = addon_dir / "user_files" / "data_files" / "pokemon_species.csv"
pokeapi_db_path = user_path_data / "pokeapi_db.json"
starters_path = addon_dir / "addon_files" / "starters.json"
eff_chart_html_path = addon_dir / "addon_files" / "eff_chart_html.html"
effectiveness_chart_file_path = addon_dir / "addon_files" / "eff_chart.json"
table_gen_id_html_path = addon_dir / "addon_files" / "table_gen_id.html"
icon_path = addon_dir / "addon_files" / "pokeball.png"
sound_list_path = addon_dir / "addon_files" / "sound_list.json"
badges_list_path = addon_dir / "addon_files" / "badges.json"
items_list_path = addon_dir / "addon_files" / "items.json"
rate_path = addon_dir / "user_files" / "rate_this.json"
csv_file_items = addon_dir / "user_files" / "data_files" / "item_names.csv"
csv_file_descriptions = addon_dir / "user_files" / "data_files" / "item_flavor_text.csv"
csv_file_items_cost = addon_dir / "user_files" / "data_files" / "items.csv"
pokemon_csv = addon_dir / "user_files" / "data_files" / "pokemon.csv"
pokemon_tm_learnset_path = addon_dir / "user_files" / "data_files" / "pokemon_tm_learnset.json"

#effect sounds paths
hurt_normal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNormal.mp3"
hurt_noteff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNotEffective.mp3"
hurt_supereff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtSuper.mp3"
ownhplow_sound_path = addon_dir / "addon_sprites" / "sounds" / "OwnHpLow.mp3"
hpheal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HpHeal.mp3"
fainted_sound_path = addon_dir / "addon_sprites" / "sounds" / "Fainted.mp3"

#pokemon species id files
pokemon_species_normal_path = addon_dir / "user_files" / "pkmn_data" / "normal.json"
pokemon_species_legendary_path = addon_dir / "user_files" / "pkmn_data" / "legendary.json"
pokemon_species_ultra_path = addon_dir / "user_files" / "pkmn_data" / "ultra.json"
pokemon_species_mythical_path = addon_dir / "user_files" / "pkmn_data" / "mythical.json"
pokemon_species_baby_path = addon_dir / "user_files" / "pkmn_data" / "baby.json"

#utils
json_file_structure = addon_dir / "addon_files" / "folder_structure.json"

#move ui paths
type_icon_path_resources = addon_dir / "addon_sprites" / "Types"

team_pokemon_path = addon_dir / "user_files" / "team.json"

#lang routes
lang_path = addon_dir / "lang"
lang_path_de = addon_dir / "lang" / "de_text.json"
lang_path_ch = addon_dir / "lang" / "ch_text.json"
lang_path_en = addon_dir / "lang" / "en_text.json"
lang_path_fr = addon_dir / "lang" / "fr_text.json"
lang_path_jp = addon_dir / "lang" / "jp_text.json"
lang_path_sp = addon_dir / "lang" / "sp_text.json"
lang_path_it = addon_dir / "lang" / "it_text.json"
lang_path_cz = addon_dir / "lang" / "cz_text.json"
lang_path_po = addon_dir / "lang" / "po_text.json"
lang_path_kr = addon_dir / "lang" / "kr_text.json"

#backup_routes
backup_root = addon_dir / "user_files" / "backups"
backup_folder_1 = backup_root / "backup_1"
backup_folder_2 = backup_root / "backup_2"
backup_folders = [os.path.join(backup_root, f"backup_{i}") for i in range(1, 4)]

#detect add-on version
try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    addon_ver = manifest.get("version", "unknown")
except Exception:
    addon_ver = "unknown"

#note if it is an experimental build
IS_EXPERIMENTAL_BUILD = addon_ver.endswith("-E")


POKEMON_TIERS = {
  "Normal": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65,
66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 143, 147, 148, 149, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186,
187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 237, 241, 242, 246, 247, 248, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280,
281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 361, 362, 363, 364, 365, 366, 367,
368, 369, 370, 371, 372, 373, 374, 375, 376, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 407, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 434, 435, 436, 437, 441, 442, 443, 444, 445, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473,
474, 475, 476, 477, 478, 479, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 568, 569, 570, 571, 572, 573, 574, 575, 576,
577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672,
673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766,
767, 768, 769, 770, 771, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878,
879, 884, 885, 886, 887],
  "Legendary": [
  # Gen 1
  144, 145, 146, 150,
  # Gen 2
  243, 244, 245, 249, 250,
  # Gen 3
  377, 378, 379, 380, 381, 382, 383, 384,
  # Gen 4
  480, 481, 482, 483, 484, 485, 486, 487, 488,
  # Gen 5
  638, 639, 640, 641, 642, 643, 644, 645, 646,
  # Gen 6
  716, 717, 718,
  # Gen 7
  772, 773, 785, 786, 787, 788, 789, 790, 791, 792, 800,
  # Gen 8
  888, 889, 890, 891, 892, 894, 895, 896, 897, 898
]
,
  "Mythical": [
  # Gen 1
  151,        # Mew
  # Gen 2
  251,        # Celebi
  # Gen 3
  385, 386,   # Jirachi, Deoxys
  # Gen 4
  489, 490, 491, 492, 493,   # Phione, Manaphy, Darkrai, Shaymin, Arceus
  # Gen 5
  494, 647, 648, 649,        # Victini, Keldeo, Meloetta, Genesect
  # Gen 6
  719, 720, 721,             # Diancie, Hoopa, Volcanion
  # Gen 7
  801, 802, 807, 808, 809,   # Magearna, Marshadow, Zeraora, Meltan, Melmetal
  # Gen 8
  893                        # Zarude
]
,
  "Ultra": [
  793,  # Nihilego
  794,  # Buzzwole
  795,  # Pheromosa
  796,  # Xurkitree
  797,  # Celesteela
  798,  # Kartana
  799,  # Guzzlord
  803,  # Poipole
  804,  # Naganadel
  805,  # Stakataka
  806   # Blacephalon
]
,
  "Fossil": [
  # Gen 1
  138, 139, 140, 141, 142,        # Omanyte, Omastar, Kabuto, Kabutops, Aerodactyl
  # Gen 3
  345, 346, 347, 348,             # Lileep, Cradily, Anorith, Armaldo
  # Gen 4
  408, 409, 410, 411,             # Cranidos, Rampardos, Shieldon, Bastiodon
  # Gen 5
  564, 565, 566, 567,             # Tirtouga, Carracosta, Archen, Archeops
  # Gen 6
  696, 697, 698, 699,             # Tyrunt, Tyrantrum, Amaura, Aurorus
  # Gen 8
  880, 881, 882, 883              # Dracozolt, Arctozolt, Dracovish, Arctovish
]
,
  "Starter": [
  # Gen 1 (Kanto)
  1, 2, 3,      # Bulbasaur, Ivysaur, Venusaur
  4, 5, 6,      # Charmander, Charmeleon, Charizard
  7, 8, 9,      # Squirtle, Wartortle, Blastoise

  # Gen 2 (Johto)
  152, 153, 154,  # Chikorita, Bayleef, Meganium
  155, 156, 157,  # Cyndaquil, Quilava, Typhlosion
  158, 159, 160,  # Totodile, Croconaw, Feraligatr

  # Gen 3 (Hoenn)
  252, 253, 254,  # Treecko, Grovyle, Sceptile
  255, 256, 257,  # Torchic, Combusken, Blaziken
  258, 259, 260,  # Mudkip, Marshtomp, Swampert

  # Gen 4 (Sinnoh)
  387, 388, 389,  # Turtwig, Grotle, Torterra
  390, 391, 392,  # Chimchar, Monferno, Infernape
  393, 394, 395,  # Piplup, Prinplup, Empoleon

  # Gen 5 (Unova)
  495, 496, 497,  # Snivy, Servine, Serperior
  498, 499, 500,  # Tepig, Pignite, Emboar
  501, 502, 503,  # Oshawott, Dewott, Samurott

  # Gen 6 (Kalos)
  650, 651, 652,  # Chespin, Quilladin, Chesnaught
  653, 654, 655,  # Fennekin, Braixen, Delphox
  656, 657, 658,  # Froakie, Frogadier, Greninja

  # Gen 7 (Alola)
  722, 723, 724,  # Rowlet, Dartrix, Decidueye
  725, 726, 727,  # Litten, Torracat, Incineroar
  728, 729, 730,  # Popplio, Brionne, Primarina

  # Gen 8 (Galar)
  810, 811, 812,  # Grookey, Thwackey, Rillaboom
  813, 814, 815,  # Scorbunny, Raboot, Cinderace
  816, 817, 818   # Sobble, Drizzile, Inteleon
]
,
  "Baby": [
    # Gen 2 (Johto)
    172,  # Pichu
    173,  # Cleffa
    174,  # Igglybuff
    175,  # Togepi
    236,  # Tyrogue
    238,  # Smoochum
    239,  # Elekid
    240,  # Magby

    # Gen 3 (Hoenn)
    298,  # Azurill
    360,  # Wynaut

    # Gen 4 (Sinnoh)
    406,  # Budew
    433,  # Chingling
    438,  # Bonsly
    439,  # Mime Jr.
    440,  # Happiny
    446,  # Munchlax
    447,  # Riolu
    458,  # Mantyke

    # Gen 8 (Galar)
    848,  # Toxel
]
,
  "Hisuian": [
    # Gen 8 (Legends: Arceus - Hisui region)
    899,  # Wyrdeer
    900,  # Kleavor
    901,  # Ursaluna
    902,  # Basculegion
    903,  # Sneasler
    904,  # Overqwil
    905,  # Enamorus
]

}

def generate_startup_files(base_path, base_user_path):  # Add base_user_path parameter
    """
    Generates blank personal files at startup with the value [].
    Introduced as a workaround to gitignore personal files.
    """
    files = ['mypokemon.json', 'mainpokemon.json', 'items.json',
             'team.json', 'data.json', 'badges.json']

    for file in files:
        file_path = os.path.join(base_user_path, file)  # Use base_user_path parameter
        # Create parent directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    # Default data for the file
    default_rating_data = {"rate_this": False}
    rate_path = os.path.join(base_user_path, 'rate_this.json')

    # Create the file with default contents if it doesn't exist
    if not os.path.exists(rate_path):
        os.makedirs(os.path.dirname(rate_path), exist_ok=True)
        with open(rate_path, "w", encoding="utf-8") as f:
            json.dump(default_rating_data, f, indent=4)

    # Create blank HelpInfos.html and updateinfos.md at base_path if they don't exist
    helpinfos_path = os.path.join(base_path, 'HelpInfos.html')
    updateinfos_path = os.path.join(base_path, 'updateinfos.md')

    if not os.path.exists(helpinfos_path):
        os.makedirs(os.path.dirname(helpinfos_path), exist_ok=True)
        with open(helpinfos_path, 'w', encoding='utf-8') as f:
            f.write('')

    if not os.path.exists(updateinfos_path):
        os.makedirs(os.path.dirname(updateinfos_path), exist_ok=True)
        with open(updateinfos_path, 'w', encoding='utf-8') as f:
            f.write('')

    return True

