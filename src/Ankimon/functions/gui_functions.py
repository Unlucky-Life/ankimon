from ..resources import type_icon_path_resources, addon_dir

def type_icon_path(type):
    png_file = f"{type}.png"
    icon_png_file_path = type_icon_path_resources / png_file
    return icon_png_file_path

def move_category_path(category):
    png_file = f"{category}_move.png"
    category_path = addon_dir / "addon_sprites" / png_file
    return category_path