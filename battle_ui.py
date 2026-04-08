import pygame
import random
import globals as g
from battle_controller import get_current_character, get_current_options, normalize_item, normalize_spell


def get_option_name(option):
    if isinstance(option, dict):
        quantity = option.get("quantity")
        if quantity is not None:
            return f"{option['name']} x{quantity}"
        return option["name"]
    return str(option)


def draw_battle(screen, state, player_image, enemy_image, player_rect, enemy_rect):
    shake_x = 0
    shake_y = 0

    if state["screen_shake"]["timer"] > 0:
        strength = state["screen_shake"]["strength"]
        shake_x = random.randint(-strength, strength)
        shake_y = random.randint(-strength, strength)
    
    current_character = get_current_character(state)
    current_enemy = state["current_enemy"]

    screen.fill(g.BLACK)
    screen.blit(enemy_image, (g.WIDTH - enemy_rect.width - 100 + shake_x, enemy_rect.y + shake_y))
    screen.blit(player_image, (250 + shake_x, player_rect.y + shake_y))

    box_width = 300
    box_height = 220
    box_x = 10
    box_y = g.HEIGHT - box_height - 140

    pygame.draw.rect(screen, g.DARK_BLUE, (box_x + 320, box_y, box_width, box_height))
    pygame.draw.rect(screen, g.WHITE, (box_x + 320, box_y, box_width, box_height), 4)

    options = get_current_options(state)
    selected_index = state["battle_menu_index"] if state["sub_menu_mode"] is None else state["sub_menu_index"]

    for i, option in enumerate(options):
        display_option = option
        if state["sub_menu_mode"] == "magic":
            display_option = normalize_spell(option)
        elif state["sub_menu_mode"] == "conjure":
            display_option = normalize_spell(option)
        elif state["sub_menu_mode"] == "item":
            display_option = normalize_item(option)

        color = g.RED if i == selected_index else g.WHITE
        text = g.small_font.render(get_option_name(display_option), True, color)
        screen.blit(text, (box_x + 340, box_y + 20 + i * 40))

    pygame.draw.rect(screen, g.DARK_BLUE, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, g.WHITE, (box_x, box_y, box_width, box_height), 4)

    pygame.draw.rect(screen, g.DARK_BLUE, (g.WIDTH - 620, box_y, 500, 170))
    pygame.draw.rect(screen, g.RED, (g.WIDTH - 620, box_y, 500, 170), 4)

    name_text = g.font.render(current_character["name"], True, g.WHITE)
    hp_text = g.small_font.render(
        f"HP: {current_character['hp']}/{current_character['max_hp']}", True, g.WHITE
    )
    mp_text = g.small_font.render(
        f"MP: {current_character['mp']}/{current_character['max_mp']}", True, g.WHITE
    )
    enemy_text = g.small_font.render(
        f"{current_enemy['name']} HP: {current_enemy['hp']}/{current_enemy['max_hp']}",
        True,
        g.WHITE,
    )

    screen.blit(name_text, (box_x + 20, box_y + 10))
    screen.blit(hp_text, (box_x + 20, box_y + 80))
    screen.blit(mp_text, (box_x + 20, box_y + 130))
    screen.blit(enemy_text, (g.WIDTH - 600, box_y + 65))

    atb_bar_width = box_width - 40
    atb_bar_height = 12
    atb_x = box_x + 20
    atb_y = box_y + box_height - 25

    pygame.draw.rect(screen, g.WHITE, (atb_x, atb_y, atb_bar_width, atb_bar_height), 2)
    atb_fill = int((current_character["atb"] / g.atb_max) * (atb_bar_width - 4))
    pygame.draw.rect(screen, g.BLUE, (atb_x + 2, atb_y + 2, atb_fill, atb_bar_height - 4))

    if state["battle_log"]:
        log_text = g.small_font.render(state["battle_log"], True, g.WHITE)
        screen.blit(log_text, (g.WIDTH // 2 - log_text.get_width() // 2, 30))

    if pygame.time.get_ticks() < state["switch_banner_until"]:
        banner = pygame.Rect(g.WIDTH // 2 - 260, 110, 520, 100)
        pygame.draw.rect(screen, g.DARK_BLUE, banner)
        pygame.draw.rect(screen, g.WHITE, banner, 4)
        switch_text = g.font.render(f"{current_character['name']}'s turn", True, g.WHITE)
        screen.blit(
            switch_text,
            (
                banner.x + banner.width // 2 - switch_text.get_width() // 2,
                banner.y + banner.height // 2 - switch_text.get_height() // 2,
            ),
        )