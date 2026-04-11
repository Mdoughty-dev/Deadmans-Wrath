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


def draw_bar(screen, x, y, width, height, current_value, max_value, fill_color, border_color):
    pygame.draw.rect(screen, g.DARK_BLUE, (x, y, width, height))
    pygame.draw.rect(screen, border_color, (x, y, width, height), 2)

    if max_value > 0:
        fill_width = int((current_value / max_value) * (width - 4))
        pygame.draw.rect(screen, fill_color, (x + 2, y + 2, fill_width, height - 4))


def draw_menu(screen, state):
    screen.fill(g.BLACK)

    party_members = get_party_members(state["characters"])

    left_rect = pygame.Rect(30, 30, 760, g.HEIGHT - 60)
    right_rect = pygame.Rect(830, 30, g.WIDTH - 860, g.HEIGHT - 60)

    pygame.draw.rect(screen, g.DARK_BLUE, left_rect)
    pygame.draw.rect(screen, g.WHITE, left_rect, 4)

    pygame.draw.rect(screen, g.DARK_BLUE, right_rect)
    pygame.draw.rect(screen, g.WHITE, right_rect, 4)

    title_left = g.font.render("PARTY", True, g.WHITE)
    title_right = g.font.render("STATUS", True, g.WHITE)

    screen.blit(title_left, (left_rect.x + 30, left_rect.y + 20))
    screen.blit(title_right, (right_rect.x + 30, right_rect.y + 20))

    if len(party_members) == 0:
        none_text = g.small_font.render("No party members", True, g.WHITE)
        screen.blit(none_text, (left_rect.x + 30, left_rect.y + 100))
        return

    if state["menu_selected_character"] >= len(party_members):
        state["menu_selected_character"] = 0

    menu_mode = state.get("menu_mode", "party")
    menu_item_index = state.get("menu_item_index", 0)

    # LEFT: party cards
    for i, member in enumerate(party_members):
        selected = i == state["menu_selected_character"] and menu_mode == "party"
        border_color = g.RED if selected else g.WHITE

        y = left_rect.y + 100 + i * 130
        card = pygame.Rect(left_rect.x + 25, y, left_rect.width - 50, 100)

        pygame.draw.rect(screen, g.BLACK, card)
        pygame.draw.rect(screen, border_color, card, 3)

        name_surface = g.small_font.render(member["name"], True, border_color)
        hp_surface = g.small_font.render(
            f"HP: {member['hp']}/{member['max_hp']}", True, g.WHITE
        )
        mp_surface = g.small_font.render(
            f"MP: {member['mp']}/{member['max_mp']}", True, g.WHITE
        )

        screen.blit(name_surface, (card.x + 20, card.y + 12))
        screen.blit(hp_surface, (card.x + 20, card.y + 45))
        screen.blit(mp_surface, (card.x + 260, card.y + 45))

    selected = party_members[state["menu_selected_character"]]

    # RIGHT: character sheet
    name_title = g.font.render(selected["name"], True, g.WHITE)
    screen.blit(name_title, (right_rect.x + 30, right_rect.y + 80))

    draw_bar(screen, right_rect.x + 30, right_rect.y + 145, 320, 24, selected["hp"], selected["max_hp"], g.RED, g.WHITE)
    draw_bar(screen, right_rect.x + 30, right_rect.y + 190, 320, 24, selected["mp"], selected["max_mp"], g.BLUE, g.WHITE)

    hp_text = g.small_font.render(f"HP {selected['hp']} / {selected['max_hp']}", True, g.WHITE)
    mp_text = g.small_font.render(f"MP {selected['mp']} / {selected['max_mp']}", True, g.WHITE)
    screen.blit(hp_text, (right_rect.x + 365, right_rect.y + 144))
    screen.blit(mp_text, (right_rect.x + 365, right_rect.y + 189))

    stats_title = g.small_font.render("Stats", True, g.WHITE)
    screen.blit(stats_title, (right_rect.x + 30, right_rect.y + 250))

    stats = selected.get("stats", {})
    stat_lines = [
        f"Attack:  {stats.get('attack', 0)}",
        f"Magic:   {stats.get('magic', 0)}",
        f"Defence: {stats.get('defence', 0)}",
        f"Speed:   {stats.get('speed', 0)}",
        f"Agility: {stats.get('agility', 0)}",
    ]

    for i, line in enumerate(stat_lines):
        txt = g.small_font.render(line, True, g.WHITE)
        screen.blit(txt, (right_rect.x + 50, right_rect.y + 290 + i * 32))

    status_title = g.small_font.render("Status Effects", True, g.WHITE)
    screen.blit(status_title, (right_rect.x + 30, right_rect.y + 470))

    effects = selected.get("status_effects", [])
    if effects:
        for i, effect in enumerate(effects):
            txt = g.small_font.render(
                f"{effect['name'].upper()} ({effect['duration']})", True, g.RED
            )
            screen.blit(txt, (right_rect.x + 50, right_rect.y + 510 + i * 30))
    else:
        txt = g.small_font.render("None", True, g.WHITE)
        screen.blit(txt, (right_rect.x + 50, right_rect.y + 510))

    # bottom right item box
    item_box = pygame.Rect(right_rect.x + 30, right_rect.y + 610, right_rect.width - 60, 220)
    pygame.draw.rect(screen, g.BLACK, item_box)
    pygame.draw.rect(screen, g.WHITE, item_box, 3)

    items_title = g.small_font.render("Shared Items", True, g.WHITE)
    screen.blit(items_title, (item_box.x + 20, item_box.y + 15))

    for i, item in enumerate(g.items):
        item_name = get_option_name(normalize_item(item))
        color = g.RED if menu_mode == "items" and i == menu_item_index else g.WHITE
        text = g.small_font.render(item_name, True, color)
        screen.blit(text, (item_box.x + 30, item_box.y + 55 + i * 30))

    controls = "UP/DOWN select  RIGHT items  LEFT back  ENTER use item  B exit"
    help_text = g.small_font.render(controls, True, g.WHITE)
    screen.blit(help_text, (right_rect.x + 30, g.HEIGHT - 55))