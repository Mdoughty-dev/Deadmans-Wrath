import pygame
import sys

def load_image(path, scale_to=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale_to:
            image = pygame.transform.scale(image, scale_to)
        return image
    except:
        print(f"❌ Could not load {path}")
        pygame.quit()
        sys.exit()

def load_assets(WIDTH, HEIGHT):
    background = load_image("assets/background.png", (WIDTH * 4, HEIGHT))
    character = load_image("assets/character.png")  # Scale later based on Rect
    enemy = load_image("assets/enemy.png")          # Scale later based on Rect
    bar = load_image("assets/bar.png") 
    return {
        "background": background,
        "character": character,
        "enemy": enemy,
        "bar" : bar
    }

