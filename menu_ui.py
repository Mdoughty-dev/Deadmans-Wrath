import pygame
import globals as g
from battle_controller import get_party_members, normalize_item, normalize_spell


def get_option_name(option):
    if isinstance(option, dict):
        quantity = option.get("quantity")
        if quantity is not None:
            return f"{option['name']} x{quantity}"
        return option["name"]
    return str(option)


def draw_menu(screen, state):
    screen.fill(g.BLACK)

    party_members = get_party_members(state["characters"])

    left_rect = pygame.Rect(0, 0, g.WIDTH // 2, g.HEIGHT)
    right_rect = pygame.Rect(g.WIDTH // 2, 0, g.WIDTH // 2, g.HEIGHT)

    pygame.draw.rect(screen, g.WHITE, left_rect, 4)
    pygame.draw.rect(screen, g.WHITE, right_rect, 4)

    pygame.draw.rect(screen, g.WHITE, (0, 0, g.WIDTH // 2, 120), 4)
    pygame.draw.rect(screen, g.WHITE, (g.WIDTH // 2, 0, g.WIDTH // 2, 120), 4)

    party_text = g.font.render("PARTY", True, g.WHITE)
    menu_text = g.font.render("MENU", True, g.WHITE)

    screen.blit(party_text, (g.WIDTH // 4 - party_text.get_width() // 2, 35))
    screen.blit(menu_text, (g.WIDTH * 3 // 4 - menu_text.get_width() // 2, 35))

    if len(party_members) == 0:
        none_text = g.small_font.render("No party members", True, g.WHITE)
        screen.blit(none_text, (80, 180))
        return

    if state["menu_selected_character"] >= len(party_members):
        state["menu_selected_character"] = 0

    for i, member in enumerate(party_members):
        color = g.RED if i == state["menu_selected_character"] else g.WHITE
        y = 180 + i * 140

        pygame.draw.rect(screen, g.DARK_BLUE, (50, y, 760, 110))
        pygame.draw.rect(screen, color, (50, y, 760, 110), 4)

        name_surface = g.small_font.render(member["name"], True, color)
        hp_surface = g.small_font.render(
            f"HP: {member['hp']}/{member['max_hp']}", True, g.WHITE
        )
        mp_surface = g.small_font.render(
            f"MP: {member['mp']}/{member['max_mp']}", True, g.WHITE
        )

        screen.blit(name_surface, (80, y + 10))
        screen.blit(hp_surface, (80, y + 45))
        screen.blit(mp_surface, (380, y + 45))

    selected = party_members[state["menu_selected_character"]]

    info_y = 160
    name_title = g.font.render(selected["name"], True, g.WHITE)
    screen.blit(name_title, (g.WIDTH // 2 + 40, info_y))

    spells_title = g.small_font.render("Spells", True, g.WHITE)
    screen.blit(spells_title, (g.WIDTH // 2 + 40, info_y + 100))

    for i, spell in enumerate(selected.get("spells", [])):
        spell_name = get_option_name(normalize_spell(spell))
        text = g.small_font.render(f"- {spell_name}", True, g.WHITE)
        screen.blit(text, (g.WIDTH // 2 + 60, info_y + 145 + i * 35))

    conjure_title = g.small_font.render("Conjures", True, g.WHITE)
    screen.blit(conjure_title, (g.WIDTH // 2 + 40, info_y + 320))

    for i, conjure in enumerate(selected.get("conjures", [])):
        conjure_name = get_option_name(normalize_spell(conjure))
        text = g.small_font.render(f"- {conjure_name}", True, g.WHITE)
        screen.blit(text, (g.WIDTH // 2 + 60, info_y + 365 + i * 35))

    items_title = g.small_font.render("Shared Items", True, g.WHITE)
    screen.blit(items_title, (g.WIDTH // 2 + 40, info_y + 520))

    for i, item in enumerate(g.items):
        item_name = get_option_name(normalize_item(item))
        text = g.small_font.render(f"- {item_name}", True, g.WHITE)
        screen.blit(text, (g.WIDTH // 2 + 60, info_y + 565 + i * 35))

    help_text = g.small_font.render("UP/DOWN = select   B = back", True, g.WHITE)
    screen.blit(help_text, (g.WIDTH // 2 + 40, g.HEIGHT - 80))