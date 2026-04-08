import pygame
import random
import globals as g
from enemies import make_creeper


def normalize_spell(spell):
    if isinstance(spell, dict):
        return spell
    return {"name": str(spell), "cost": 0, "damage": 0}


def normalize_item(item):
    if isinstance(item, dict):
        return item

    name = str(item).lower()
    if name == "potion":
        return {"name": "Potion", "heal": 40, "quantity": 1}

    return {"name": str(item), "quantity": 1}


def get_party_members(characters):
    return [member for member in characters if member.get("in_party", False)]

def start_attack_motion(state, player):
    motion = state["attack_motion"]
    motion["active"] = True
    motion["phase"] = "forward"
    motion["timer"] = 0
    motion["start_x"] = player.x
    motion["damage_applied"] = False
    motion["return_to_idle"] = True

    state["player_visual_state"]["action"] = "attack"
    state["player_visual_state"]["frame_index"] = 0
    state["player_visual_state"]["frame_timer"] = 0

def trigger_hit_effects(state):
    state["hit_pause"] = 5
    state["screen_shake"]["timer"] = 8
    state["screen_shake"]["strength"] = 8

def update_attack_motion(state, player, enemy):
    motion = state["attack_motion"]

    if not motion["active"]:
        return

    if state["hit_pause"] > 0:
        return

    motion["timer"] += 1

    t = motion["timer"] / motion["duration"]
    if t > 1:
        t = 1

    progress = t * t * (3 - 2 * t)  # smoothstep

    if motion["phase"] == "forward":
        player.x = motion["start_x"] + motion["distance"] * progress

        if t >= 0.6 and not motion["damage_applied"]:
            state["current_enemy"]["hp"] -= 20
            state["battle_log"] = f"{get_current_character(state)['name']} attacks for 20 damage!"
            motion["damage_applied"] = True

            enemy.x += 12
            trigger_hit_effects(state)

        if t >= 1:
            motion["phase"] = "back"
            motion["timer"] = 0

    elif motion["phase"] == "back":
        player.x = motion["start_x"] + motion["distance"] * (1 - progress)

        if t >= 1:
            player.x = motion["start_x"]
            motion["active"] = False
            get_current_character(state)["atb"] = 0
            state["player_turn"] = False

            if motion["return_to_idle"]:
                state["player_visual_state"]["action"] = "idle"

            queue_next_character(state)

def update_hit_pause_and_shake(state):
    if state["hit_pause"] > 0:
        state["hit_pause"] -= 1

    if state["screen_shake"]["timer"] > 0:
        state["screen_shake"]["timer"] -= 1
        if state["screen_shake"]["timer"] == 0:
            state["screen_shake"]["strength"] = 0


def get_alive_party_indices(characters):
    alive = []
    for i, member in enumerate(characters):
        if member.get("in_party", False) and member["hp"] > 0:
            alive.append(i)
    return alive


def get_next_alive_character_index(characters, start_index):
    alive = get_alive_party_indices(characters)

    if not alive:
        return None

    if start_index not in alive:
        return alive[0]

    current_pos = alive.index(start_index)
    next_pos = (current_pos + 1) % len(alive)
    return alive[next_pos]


def get_current_character(state):
    return state["characters"][state["current_character_index"]]


def get_current_options(state):
    current_character = get_current_character(state)

    if state["sub_menu_mode"] == "magic":
        return current_character.get("spells", [])
    if state["sub_menu_mode"] == "conjure":
        return current_character.get("conjures", [])
    if state["sub_menu_mode"] == "item":
        return g.items
    return g.menu_options


def start_battle(state, player, enemy, original_player_image, creeper_image):
    state["game_state"] = g.STATE_BATTLE
    state["sub_menu_mode"] = None
    state["sub_menu_index"] = 0
    state["battle_menu_index"] = 0
    state["player_turn"] = False
    state["switch_banner_until"] = 0
    state["battle_log"] = ""
    state["current_enemy"] = make_creeper()

    for member in state["characters"]:
        member["atb"] = 0

    state["current_enemy"]["atb"] = 0
    state["current_enemy"]["turn"] = False
    state["current_enemy"]["attack_index"] = 0

    alive = get_alive_party_indices(state["characters"])
    if alive:
        state["current_character_index"] = alive[0]

    player.x = 450
    player.y = 175
    enemy.y = 175
    enemy.x -= 150

    player.width = player.width * 2
    player.height = player.height * 2
    enemy.width = enemy.width * 2
    enemy.height = enemy.height * 2

    player_image = pygame.transform.scale(
        original_player_image, (int(player.width), int(player.height))
    )
    enemy_image = pygame.transform.scale(
        creeper_image, (int(enemy.width), int(enemy.height))
    )

    return player_image, enemy_image


def end_battle_win(state, player, enemy, original_player_image):
    state["battle_log"] = "Enemy defeated!"
    state["game_state"] = g.STATE_EXPLORE
    state["sub_menu_mode"] = None
    state["player_turn"] = False

    enemy.x = 10000
    player.y = 450
    player.x = 1800
    player.width = player.width / 2
    player.height = player.height / 2

    return pygame.transform.scale(
        original_player_image, (int(player.width), int(player.height))
    )


def end_battle_loss(state):
    state["battle_log"] = "Game Over!"


def queue_next_character(state):
    next_index = get_next_alive_character_index(
        state["characters"], state["current_character_index"]
    )

    if next_index is not None:
        state["current_character_index"] = next_index
        state["switch_banner_until"] = pygame.time.get_ticks() + 1000
        state["player_turn"] = False
        state["sub_menu_mode"] = None
        state["sub_menu_index"] = 0


def perform_attack(state, player):
    current_character = get_current_character(state)

    if state["attack_motion"]["active"]:
        return

    state["battle_log"] = f"{current_character['name']} attacks!"
    start_attack_motion(state, player)


def perform_magic(state):
    current_character = get_current_character(state)
    spell = normalize_spell(current_character["spells"][state["sub_menu_index"]])

    if current_character["mp"] < spell.get("cost", 0):
        state["battle_log"] = "Not enough MP!"
        return

    current_character["mp"] -= spell.get("cost", 0)

    if "damage" in spell and spell["damage"] > 0:
        state["current_enemy"]["hp"] -= spell["damage"]
        state["battle_log"] = f"{current_character['name']} casts {spell['name']}!"
    elif "heal" in spell and spell["heal"] > 0:
        current_character["hp"] = min(
            current_character["max_hp"],
            current_character["hp"] + spell["heal"],
        )
        state["battle_log"] = f"{current_character['name']} casts {spell['name']}!"
    else:
        state["battle_log"] = f"{current_character['name']} uses {spell['name']}!"

    current_character["atb"] = 0
    state["player_turn"] = False
    state["sub_menu_mode"] = None
    queue_next_character(state)


def perform_conjure(state):
    current_character = get_current_character(state)
    conjure = normalize_spell(current_character["conjures"][state["sub_menu_index"]])

    if current_character["mp"] < conjure.get("cost", 0):
        state["battle_log"] = "Not enough MP!"
        return

    current_character["mp"] -= conjure.get("cost", 0)
    state["current_enemy"]["hp"] -= conjure.get("damage", 0)
    state["battle_log"] = f"{current_character['name']} conjures {conjure['name']}!"
    current_character["atb"] = 0
    state["player_turn"] = False
    state["sub_menu_mode"] = None
    queue_next_character(state)


def perform_item(state):
    current_character = get_current_character(state)
    item = normalize_item(g.items[state["sub_menu_index"]])

    if item.get("quantity", 0) <= 0:
        state["battle_log"] = "No more left!"
        return

    if "heal" in item:
        current_character["hp"] = min(
            current_character["max_hp"],
            current_character["hp"] + item["heal"],
        )
        state["battle_log"] = f"{current_character['name']} used {item['name']}!"
    elif "mp_restore" in item:
        current_character["mp"] = min(
            current_character["max_mp"],
            current_character["mp"] + item["mp_restore"],
        )
        state["battle_log"] = f"{current_character['name']} used {item['name']}!"
    else:
        state["battle_log"] = f"{current_character['name']} used {item['name']}!"

    if isinstance(g.items[state["sub_menu_index"]], dict):
        g.items[state["sub_menu_index"]]["quantity"] -= 1

    current_character["atb"] = 0
    state["player_turn"] = False
    state["sub_menu_mode"] = None
    queue_next_character(state)


def enemy_take_turn(state):
    current_character = get_current_character(state)
    current_enemy = state["current_enemy"]
    attack = current_enemy["attack_cycle"][current_enemy["attack_index"]]

    if attack == "Knife Stab":
        damage = 25
    elif attack == "Knife Fury":
        damage = 35
    else:
        damage = 20

    current_character["hp"] -= damage
    state["battle_log"] = f"{current_enemy['name']} uses {attack} for {damage} damage!"

    current_enemy["attack_index"] = (
        current_enemy["attack_index"] + 1
    ) % len(current_enemy["attack_cycle"])
    current_enemy["atb"] = 0
    current_enemy["turn"] = False


def handle_battle_input(event, state, player):
    if event.type != pygame.KEYDOWN:
        return

    now = pygame.time.get_ticks()

    if now < state["switch_banner_until"]:
        return

    if not state["player_turn"]:
        return

    current_character = get_current_character(state)
    options = get_current_options(state)

    if event.key == pygame.K_DOWN:
        if state["sub_menu_mode"] is None:
            state["battle_menu_index"] = (
                state["battle_menu_index"] + 1
            ) % len(g.menu_options)
        else:
            if len(options) > 0:
                state["sub_menu_index"] = (state["sub_menu_index"] + 1) % len(options)

    elif event.key == pygame.K_UP:
        if state["sub_menu_mode"] is None:
            state["battle_menu_index"] = (
                state["battle_menu_index"] - 1
            ) % len(g.menu_options)
        else:
            if len(options) > 0:
                state["sub_menu_index"] = (state["sub_menu_index"] - 1) % len(options)

    elif event.key == pygame.K_ESCAPE:
        state["sub_menu_mode"] = None
        state["sub_menu_index"] = 0

    elif event.key == pygame.K_RETURN:
        if state["sub_menu_mode"] is None:
            action = g.menu_options[state["battle_menu_index"]]

            if action == "Attack":
                perform_attack(state, player)

            elif action == "Magic":
                if len(current_character.get("spells", [])) > 0:
                    state["sub_menu_mode"] = "magic"
                    state["sub_menu_index"] = 0
                else:
                    state["battle_log"] = "No spells."

            elif action == "Conjure":
                if len(current_character.get("conjures", [])) > 0:
                    state["sub_menu_mode"] = "conjure"
                    state["sub_menu_index"] = 0
                else:
                    state["battle_log"] = "No conjures."

            elif action == "Item":
                if len(g.items) > 0:
                    state["sub_menu_mode"] = "item"
                    state["sub_menu_index"] = 0
                else:
                    state["battle_log"] = "No items."
        else:
            if len(options) > 0:
                if state["sub_menu_mode"] == "magic":
                    perform_magic(state)
                elif state["sub_menu_mode"] == "conjure":
                    perform_conjure(state)
                elif state["sub_menu_mode"] == "item":
                    perform_item(state)


def update_battle(state, player, enemy):
    update_hit_pause_and_shake(state)
    update_attack_motion(state, player, enemy)

    if state["attack_motion"]["active"] or state["hit_pause"] > 0:
        return
    now = pygame.time.get_ticks()
    current_character = get_current_character(state)
    current_enemy = state["current_enemy"]

    if not state["player_turn"] and now >= state["switch_banner_until"]:
        current_character["atb"] += 0.5
        if current_character["atb"] >= g.atb_max:
            current_character["atb"] = g.atb_max
            state["player_turn"] = True

    if not state["player_turn"] and not current_enemy["turn"] and now >= state["switch_banner_until"]:
        current_enemy["atb"] += 0.35
        if current_enemy["atb"] >= g.atb_max:
            current_enemy["turn"] = True

    if current_enemy["turn"] and not state["player_turn"] and now >= state["switch_banner_until"]:
        enemy_take_turn(state)

        if current_character["hp"] <= 0:
            next_idx = get_next_alive_character_index(
                state["characters"], state["current_character_index"]
            )
            if next_idx is not None and next_idx != state["current_character_index"]:
                state["current_character_index"] = next_idx
                state["switch_banner_until"] = pygame.time.get_ticks() + 1000