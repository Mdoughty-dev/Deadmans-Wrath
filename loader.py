import pygame
import sys
import os


def load_animation_folder(folder_path):
    frames = []

    for file in sorted(os.listdir(folder_path)):
        if file.endswith(".png"):
            path = os.path.join(folder_path, file)
            frames.append(load_image(path))

    return frames


def load_image(path, scale_to=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale_to:
            image = pygame.transform.scale(image, scale_to)
        return image
    except Exception as e:
        print(f"❌ Could not load {path}: {e}")
        pygame.quit()
        sys.exit()


def build_player_animations():
    idle_down = load_animation_folder("assets/player/idle_down")
    idle_up = load_animation_folder("assets/player/idle_up")
    idle_right = load_animation_folder("assets/player/idle_right")

    walk_down = load_animation_folder("assets/player/walk_down")
    walk_up = load_animation_folder("assets/player/walk_up")
    walk_right = load_animation_folder("assets/player/walk_right")

    # Flip right → left
    idle_left = [pygame.transform.flip(f, True, False) for f in idle_right]
    walk_left = [pygame.transform.flip(f, True, False) for f in walk_right]

    return {
        "idle_down": idle_down,
        "idle_up": idle_up,
        "idle_right": idle_right,
        "idle_left": idle_left,
        "walk_down": walk_down,
        "walk_up": walk_up,
        "walk_right": walk_right,
        "walk_left": walk_left,
    }


def scale_animation_set(animation_set, size):
    """
    Returns a scaled copy of an animation set.
    Useful when the player rect changes size between scenes.
    """
    scaled = {}

    for key, frames in animation_set.items():
        scaled[key] = [pygame.transform.scale(frame, size) for frame in frames]

    return scaled


def load_assets(width, height):
    background = load_image("assets/background.png", (width * 4, height))
    character = load_image("assets/character.png")
    enemy = load_image("assets/enemy.png")
    bar = load_image("assets/bar.png", (width, height))

    character_animations = build_player_animations()
    spell_images = {
        "hex": load_image("assets/spells/hex.png", (400, 550))
    }

    return {
        "background": background,
        "character": character,
        "character_animations": character_animations,
        "enemy": enemy,
        "bar": bar,
        "spell_images" : spell_images,
    }