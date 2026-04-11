import pygame
import globals as g
from enemies import make_creeper


# =========================
# BASIC HELPERS
# =========================

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


def get_current_enemy(state):
    return state["current_enemy"]


def get_current_options(state):
    current_character = get_current_character(state)

    if state["sub_menu_mode"] == "magic":
        return current_character.get("spells", [])
    if state["sub_menu_mode"] == "conjure":
        return current_character.get("conjures", [])
    if state["sub_menu_mode"] == "item":
        return g.items
    return g.menu_options

def has_status_effect(target, effect_name):
    return any(effect["name"] == effect_name for effect in target.get("status_effects", []))


def add_status_effect(target, effect_name, duration):
    if has_status_effect(target, effect_name):
        for effect in target["status_effects"]:
            if effect["name"] == effect_name:
                effect["duration"] = max(effect["duration"], duration)
        return

    target.setdefault("status_effects", []).append({
        "name": effect_name,
        "duration": duration,
    })





# =========================
# BATTLE FLOW HELPERS
# =========================

def reset_menu_state(state):
    state["sub_menu_mode"] = None
    state["sub_menu_index"] = 0
    state["battle_menu_index"] = 0


def end_player_turn(state, queue_next=True):
    current_character = get_current_character(state)
    current_character["atb"] = 0
    state["player_turn"] = False
    state["sub_menu_mode"] = None
    state["sub_menu_index"] = 0

    if queue_next:
        queue_next_character(state)


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


def can_accept_input(state):
    now = pygame.time.get_ticks()

    if now < state["switch_banner_until"]:
        return False

    if not state["player_turn"]:
        return False

    if state["attack_motion"]["active"] or state["spell_projectile"]["active"]:
        return False

    return True

def resolve_enemy_attack(attacker, defender, attack):
    damage = 0

    if attack.get("damage", 0) > 0:
        if attack.get("type") == "magic":
            damage = calculate_magic_damage(attacker, defender, attack)
        else:
            damage = calculate_physical_damage(attacker, defender, attack)

        apply_damage(defender, damage)

    if attack.get("heal", 0) > 0:
        heal_target(attacker, attack["heal"])

    effect = attack.get("effect")
    if effect:
        duration = attack.get("duration", 3)
        add_status_effect(defender, effect, duration)

    return damage

def use_menu_item_on_character(state):
    party_members = get_party_members(state["characters"])
    if not party_members:
        state["battle_log"] = "No party members."
        return

    selected_character = party_members[state["menu_selected_character"]]

    if len(g.items) == 0:
        state["battle_log"] = "No items."
        return

    item_index = state["menu_item_index"]
    item = normalize_item(g.items[item_index])

    if item.get("quantity", 0) <= 0:
        state["battle_log"] = "No more left!"
        return

    used = False

    if "heal" in item:
        if selected_character["hp"] < selected_character["max_hp"]:
            selected_character["hp"] = min(
                selected_character["max_hp"],
                selected_character["hp"] + item["heal"],
            )
            used = True
    elif "mp_restore" in item:
        if selected_character["mp"] < selected_character["max_mp"]:
            selected_character["mp"] = min(
                selected_character["max_mp"],
                selected_character["mp"] + item["mp_restore"],
            )
            used = True

    if not used:
        state["battle_log"] = f"{selected_character['name']} cannot use {item['name']} right now."
        return

    if isinstance(g.items[item_index], dict):
        g.items[item_index]["quantity"] -= 1

    state["battle_log"] = f"{selected_character['name']} used {item['name']}!"
# =========================
# STATS / DAMAGE
# =========================

def calculate_physical_damage(attacker, defender, attack=None):
    attack_stat = attacker.get("stats", {}).get("attack", 20)
    defence = get_effective_defence(defender)
    move_power = 0
    if attack:
        move_power = attack.get("damage", 0)
    damage = attack_stat + move_power - int(defence * 0.5)
    return max(1, damage)


def calculate_magic_damage(attacker, defender, spell):
    magic = attacker.get("stats", {}).get("magic", 0)
    defence = get_effective_defence(defender)
    move_power = spell.get("damage", 0)
    damage = magic + move_power - int(defence * 0.3)
    return max(1, damage)

   

def get_effective_defence(target):
    defence = target.get("stats", {}).get("defence", 0)

    if has_status_effect(target, "hex"):
        defence = max(0, defence - 3)

    return defence


def apply_damage(target, amount):
    target["hp"] = max(0, target["hp"] - amount)


def heal_target(target, amount):
    target["hp"] = min(target["max_hp"], target["hp"] + amount)

def process_status_effects(target, state=None):
    remaining = []

    for effect in target.get("status_effects", []):

        if effect["name"] == "poison":
            damage = int(target["max_hp"] * 0.05)
            target["hp"] -= damage

            if state:
                state["battle_log"] = f"{target['name']} takes {damage} poison damage!"

        elif effect["name"] == "burn":
            damage = 8
            target["hp"] -= damage

            if state:
                state["battle_log"] = f"{target['name']} is burned for {damage}!"

        elif effect["name"] == "hex":
            # no direct damage, handled in defence calculation
            pass

        effect["duration"] -= 1

        if effect["duration"] > 0:
            remaining.append(effect)

    target["status_effects"] = remaining


# =========================
# BATTLE SETUP
# =========================

def start_battle(state, player, enemy, original_player_image, creeper_image):
    state["game_state"] = g.STATE_BATTLE
    reset_menu_state(state)
    state["player_turn"] = False
    state["switch_banner_until"] = 0
    state["battle_log"] = ""
    state["current_enemy"] = make_creeper()
    state["spell_projectile"]["active"] = False

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


# =========================
# INPUT
# =========================

def handle_battle_input(event, state, player, enemy):
    if event.type != pygame.KEYDOWN:
        return

    if not can_accept_input(state):
        return

    current_character = get_current_character(state)
    options = get_current_options(state)

    if event.key == pygame.K_DOWN:
        move_menu_down(state, options)

    elif event.key == pygame.K_UP:
        move_menu_up(state, options)

    elif event.key == pygame.K_ESCAPE:
        state["sub_menu_mode"] = None
        state["sub_menu_index"] = 0

    elif event.key == pygame.K_RETURN:
        if state["sub_menu_mode"] is None:
            handle_main_menu_selection(state, player, enemy, current_character)
        else:
            handle_sub_menu_selection(state, player, enemy, options)


def move_menu_down(state, options):
    if state["sub_menu_mode"] is None:
        state["battle_menu_index"] = (state["battle_menu_index"] + 1) % len(g.menu_options)
    elif len(options) > 0:
        state["sub_menu_index"] = (state["sub_menu_index"] + 1) % len(options)


def move_menu_up(state, options):
    if state["sub_menu_mode"] is None:
        state["battle_menu_index"] = (state["battle_menu_index"] - 1) % len(g.menu_options)
    elif len(options) > 0:
        state["sub_menu_index"] = (state["sub_menu_index"] - 1) % len(options)


def handle_main_menu_selection(state, player, enemy, current_character):
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


def handle_sub_menu_selection(state, player, enemy, options):
    if len(options) == 0:
        return

    if state["sub_menu_mode"] == "magic":
        perform_magic(state, player, enemy)
    elif state["sub_menu_mode"] == "conjure":
        perform_conjure(state)
    elif state["sub_menu_mode"] == "item":
        perform_item(state)


# =========================
# UPDATE LOOP
# =========================

def update_battle(state, player, enemy):
    update_hit_pause_and_shake(state)
    update_attack_motion(state, player, enemy)
    update_spell_projectile(state, enemy)

    if battle_animation_active(state):
        return

    now = pygame.time.get_ticks()
    current_character = get_current_character(state)
    current_enemy = get_current_enemy(state)

    update_player_atb(state, current_character, now)
    update_enemy_atb(state, current_enemy, now)
    resolve_enemy_turn_if_ready(state, current_character, current_enemy)


def battle_animation_active(state):
    return (
        state["attack_motion"]["active"]
        or state["spell_projectile"]["active"]
        or state["hit_pause"] > 0
    )

def update_player_atb(state, current_character, now):
    if not state["player_turn"] and now >= state["switch_banner_until"]:
        speed = current_character.get("stats", {}).get("speed", 10)
        current_character["atb"] += speed * 0.05
        if current_character["atb"] >= g.atb_max:
            current_character["atb"] = g.atb_max
            process_status_effects(current_character, state)
            state["player_turn"] = True
            


def update_enemy_atb(state, current_enemy, now):
    if not state["player_turn"] and not current_enemy["turn"] and now >= state["switch_banner_until"]:
        speed = current_enemy.get("stats", {}).get("speed", 10)
        current_enemy["atb"] += speed * 0.05
        if current_enemy["atb"] >= g.atb_max:
            process_status_effects(current_enemy, state)
            current_enemy["turn"] = True


def resolve_enemy_turn_if_ready(state, current_character, current_enemy):
    now = pygame.time.get_ticks()

    if current_enemy["turn"] and not state["player_turn"] and now >= state["switch_banner_until"]:
        enemy_take_turn(state)

        if current_character["hp"] <= 0:
            next_idx = get_next_alive_character_index(
                state["characters"], state["current_character_index"]
            )
            if next_idx is not None and next_idx != state["current_character_index"]:
                state["current_character_index"] = next_idx
                state["switch_banner_until"] = pygame.time.get_ticks() + 1000


# =========================
# ATTACK ACTIONS
# =========================

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


def perform_attack(state, player):
    if state["attack_motion"]["active"]:
        return

    current_character = get_current_character(state)
    state["battle_log"] = f"{current_character['name']} attacks!"
    start_attack_motion(state, player)


def update_attack_motion(state, player, enemy):
    motion = state["attack_motion"]

    if not motion["active"]:
        return

    if state["hit_pause"] > 0:
        return

    motion["timer"] += 1
    t = min(1, motion["timer"] / motion["duration"])
    progress = t * t * (3 - 2 * t)

    if motion["phase"] == "forward":
        update_attack_forward_phase(state, player, enemy, motion, progress, t)
    elif motion["phase"] == "back":
        update_attack_back_phase(state, player, motion, progress, t)


def update_attack_forward_phase(state, player, enemy, motion, progress, t):
    player.x = motion["start_x"] + motion["distance"] * progress

    if t >= 0.6 and not motion["damage_applied"]:
        attacker = get_current_character(state)
        defender = get_current_enemy(state)
        damage = calculate_physical_damage(attacker, defender, {"damage": 15})

        apply_damage(defender, damage)
        state["battle_log"] = f"{attacker['name']} attacks for {damage} damage!"
        motion["damage_applied"] = True

        enemy.x += 12
        trigger_hit_effects(state)

    if t >= 1:
        motion["phase"] = "back"
        motion["timer"] = 0


def update_attack_back_phase(state, player, motion, progress, t):
    player.x = motion["start_x"] + motion["distance"] * (1 - progress)

    if t >= 1:
        player.x = motion["start_x"]
        motion["active"] = False
        end_player_turn(state, queue_next=True)

        if motion["return_to_idle"]:
            state["player_visual_state"]["action"] = "idle"


# =========================
# HIT EFFECTS
# =========================

def trigger_hit_effects(state):
    state["hit_pause"] = 5
    state["screen_shake"]["timer"] = 8
    state["screen_shake"]["strength"] = 8


def update_hit_pause_and_shake(state):
    if state["hit_pause"] > 0:
        state["hit_pause"] -= 1

    if state["screen_shake"]["timer"] > 0:
        state["screen_shake"]["timer"] -= 1
        if state["screen_shake"]["timer"] == 0:
            state["screen_shake"]["strength"] = 0


# =========================
# MAGIC / PROJECTILES
# =========================

def start_spell_projectile(state, player, enemy, spell):
    projectile = state["spell_projectile"]
    projectile["active"] = True
    projectile["spell_name"] = spell["name"]
    projectile["spell_data"] = spell
    projectile["effect"] = spell.get("effect", "")
    projectile["damage"] = spell.get("damage", 0)
    projectile["x"] = player.x + player.width - 20
    projectile["y"] = player.y + player.height // 2
    projectile["target_x"] = g.WIDTH - enemy.width - 100 + enemy.width // 2
    projectile["target_y"] = enemy.y + enemy.height // 2
    projectile["speed"] = spell.get("projectile_speed", 24)
    projectile["damage_applied"] = False


def perform_magic(state, player, enemy):
    current_character = get_current_character(state)
    spell = normalize_spell(current_character["spells"][state["sub_menu_index"]])

    if current_character["mp"] < spell.get("cost", 0):
        state["battle_log"] = "Not enough MP!"
        return

    current_character["mp"] -= spell.get("cost", 0)

    if spell.get("effect") and spell.get("damage", 0) > 0:
        start_spell_projectile(state, player, enemy, spell)
        state["battle_log"] = f"{current_character['name']} casts {spell['name']}!"
        state["sub_menu_mode"] = None
        return

    if spell.get("damage", 0) > 0:
        damage = calculate_magic_damage(current_character, get_current_enemy(state), spell)
        apply_damage(state["current_enemy"], damage)
        state["battle_log"] = f"{current_character['name']} casts {spell['name']} for {damage} damage!"

    elif spell.get("heal", 0) > 0:
        heal_target(current_character, spell["heal"])
        state["battle_log"] = f"{current_character['name']} casts {spell['name']}!"

    else:
        state["battle_log"] = f"{current_character['name']} uses {spell['name']}!"

    end_player_turn(state, queue_next=True)


def update_spell_projectile(state, enemy):
    projectile = state["spell_projectile"]

    if not projectile["active"]:
        return

    dx = projectile["target_x"] - projectile["x"]
    dy = projectile["target_y"] - projectile["y"]
    distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)

    if distance <= projectile["speed"]:
        finish_spell_projectile(state, enemy)
        return

    projectile["x"] += dx / distance * projectile["speed"]
    projectile["y"] += dy / distance * projectile["speed"]


def finish_spell_projectile(state, enemy):
    projectile = state["spell_projectile"]
    projectile["x"] = projectile["target_x"]
    projectile["y"] = projectile["target_y"]

    if not projectile["damage_applied"]:
        attacker = get_current_character(state)
        defender = get_current_enemy(state)
        spell = projectile.get("spell_data", {"damage": projectile["damage"]})
        damage = calculate_magic_damage(attacker, defender, spell)

        apply_damage(defender, damage)
        state["battle_log"] = f"{attacker['name']} casts {projectile['spell_name']} for {damage} damage!"
        projectile["damage_applied"] = True

        if projectile["effect"] == "hex":
            add_status_effect(defender, "hex", 3)

        enemy.x += 12
        trigger_hit_effects(state)

    projectile["active"] = False
    end_player_turn(state, queue_next=True)


# =========================
# CONJURE / ITEMS
# =========================

def perform_conjure(state):
    current_character = get_current_character(state)
    conjure = normalize_spell(current_character["conjures"][state["sub_menu_index"]])

    if current_character["mp"] < conjure.get("cost", 0):
        state["battle_log"] = "Not enough MP!"
        return

    current_character["mp"] -= conjure.get("cost", 0)

    damage = calculate_magic_damage(current_character, get_current_enemy(state), conjure)
    apply_damage(state["current_enemy"], damage)
    state["battle_log"] = f"{current_character['name']} conjures {conjure['name']} for {damage} damage!"

    end_player_turn(state, queue_next=True)


def perform_item(state):
    current_character = get_current_character(state)
    item = normalize_item(g.items[state["sub_menu_index"]])

    if item.get("quantity", 0) <= 0:
        state["battle_log"] = "No more left!"
        return

    use_item_on_character(current_character, item)
    decrement_global_item_quantity(state)
    end_player_turn(state, queue_next=True)


def use_item_on_character(current_character, item):
    if "heal" in item:
        heal_target(current_character, item["heal"])
    elif "mp_restore" in item:
        current_character["mp"] = min(
            current_character["max_mp"],
            current_character["mp"] + item["mp_restore"],
        )


def decrement_global_item_quantity(state):
    item_index = state["sub_menu_index"]
    current_character = get_current_character(state)
    item = normalize_item(g.items[item_index])

    state["battle_log"] = f"{current_character['name']} used {item['name']}!"

    if isinstance(g.items[item_index], dict):
        g.items[item_index]["quantity"] -= 1


# =========================
# ENEMY ACTIONS
# =========================




def enemy_take_turn(state):
    current_character = get_current_character(state)
    current_enemy = get_current_enemy(state)

    attack = current_enemy["attacks"][current_enemy["attack_index"]]
    damage = resolve_enemy_attack(current_enemy, current_character, attack)

    if attack.get("heal", 0) > 0 and damage <= 0:
        state["battle_log"] = (
            f"{current_enemy['name']} uses {attack['name']} and heals for {attack['heal']}!"
        )
    elif attack.get("effect") and damage > 0:
        state["battle_log"] = (
            f"{current_enemy['name']} uses {attack['name']} for {damage} damage and inflicts {attack['effect']}!"
        )
    elif attack.get("effect"):
        state["battle_log"] = (
            f"{current_enemy['name']} uses {attack['name']} and inflicts {attack['effect']}!"
        )
    else:
        state["battle_log"] = (
            f"{current_enemy['name']} uses {attack['name']} for {damage} damage!"
        )

    current_enemy["attack_index"] = (
        current_enemy["attack_index"] + 1
    ) % len(current_enemy["attacks"])

    current_enemy["atb"] = 0
    current_enemy["turn"] = False


# =========================
# BATTLE END
# =========================

def end_battle_win(state, player, enemy, original_player_image):
    state["battle_log"] = "Enemy defeated!"
    state["game_state"] = g.STATE_EXPLORE
    state["sub_menu_mode"] = None
    state["player_turn"] = False
    state["spell_projectile"]["active"] = False

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



















