import pygame
import sys
from loader import load_assets, scale_animation_set
import globals as g
from characters import characters
from enemies import make_creeper

from battle_controller import (
    get_alive_party_indices,
    get_party_members,
    handle_battle_input,
    update_battle,
    end_battle_loss,
    end_battle_win,
)
from battle_ui import draw_battle
from menu_ui import draw_menu
from explore_controller import update_explore, draw_explore, handle_explore_keys
from bar_controller import handle_bar_input, update_bar, draw_bar, leave_bar
from player_visuals import (
    update_player_animation,
    get_current_player_frame,
    reset_player_visual_state,
)

pygame.init()

screen = pygame.display.set_mode((g.WIDTH, g.HEIGHT))
pygame.display.set_caption("The Deformed")
clock = pygame.time.Clock()

assets = load_assets(g.WIDTH, g.HEIGHT)
background = assets["background"]
original_player_image = assets["character"]
base_player_animations = assets["character_animations"]
creeper_image_source = assets["enemy"]
bar = assets["bar"]

player = pygame.Rect(600, (g.HEIGHT / 2) - (g.HEIGHT / 8), g.HEIGHT / 8, g.HEIGHT / 4)
player_image = pygame.transform.scale(
    original_player_image, (int(player.width), int(player.height))
)

enemy = pygame.Rect(1800, (g.HEIGHT / 2) - (g.HEIGHT / 8), g.HEIGHT / 8, g.HEIGHT / 4)
enemy_image = pygame.transform.scale(
    creeper_image_source, (int(enemy.width), int(enemy.height))
)

character_rect = pygame.Rect(300, 200, 300, 300)
door_rect = pygame.Rect(1400, g.HEIGHT - 625, 80, 150)

character_speech = ["hello", "how are you", "what do you want"]

state = {
    "game_state": g.STATE_EXPLORE,
    "camera_x": 0,
    "battle_menu_index": 0,
    "sub_menu_index": 0,
    "sub_menu_mode": None,
    "battle_log": "",
    "player_turn": False,
    "switch_banner_until": 0,
    "menu_selected_character": 0,
    "current_enemy": make_creeper(),
    "current_character_index": 0,
    "characters": characters,
    "show_dialogue": False,
    "dialogue_tracker": 0,
    "player_visual_state": {
        "action": "idle",
        "facing": "right",
        "frame_index": 0,
        "frame_timer": 0,
        "animation_speed": 10,
    },
}

player_animations = scale_animation_set(
    base_player_animations,
    (int(player.width), int(player.height))
)

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state["game_state"] == g.STATE_BATTLE:
            handle_battle_input(event, state)

        if state["game_state"] == g.STATE_BAR:
            handle_bar_input(event, state, player, character_speech, character_rect)

        if state["game_state"] == g.STATE_MENU and event.type == pygame.KEYDOWN:
            party_members = get_party_members(state["characters"])

            if len(party_members) > 0:
                if event.key == pygame.K_DOWN:
                    state["menu_selected_character"] = (
                        state["menu_selected_character"] + 1
                    ) % len(party_members)
                elif event.key == pygame.K_UP:
                    state["menu_selected_character"] = (
                        state["menu_selected_character"] - 1
                    ) % len(party_members)

            if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
                state["game_state"] = g.STATE_EXPLORE
                reset_player_visual_state(state, action="idle")

    if state["game_state"] == g.STATE_EXPLORE:
        update_explore(state, keys, player, background)
        update_player_animation(state, player_animations)
        current_player_frame = get_current_player_frame(
            state, player_animations, player_image
        )

        draw_explore(
            screen,
            state,
            background,
            enemy_image,
            current_player_frame,
            player,
            enemy,
            door_rect,
        )

        player_image, enemy_image = handle_explore_keys(
            state,
            keys,
            screen,
            enemy,
            player,
            door_rect,
            original_player_image,
            creeper_image_source,
            player_image,
            enemy_image,
        )

        player_animations = scale_animation_set(
            base_player_animations,
            (int(player.width), int(player.height))
        )

    elif state["game_state"] == g.STATE_BATTLE:
        reset_player_visual_state(state, action="idle")
        update_battle(state)
        draw_battle(screen, state, player_image, enemy_image, player, enemy)

        if len(get_alive_party_indices(state["characters"])) == 0:
            end_battle_loss(state)
            print("Game Over!")
            running = False

        if state["current_enemy"]["hp"] <= 0:
            print("Enemy defeated!")
            player_image = end_battle_win(state, player, enemy, original_player_image)

            player_animations = scale_animation_set(
                base_player_animations,
                (int(player.width), int(player.height))
            )

        if keys[pygame.K_r]:
            state["game_state"] = g.STATE_EXPLORE
            player.x = 600
            player.width = g.HEIGHT / 8
            player.height = g.HEIGHT / 4
            player_image = pygame.transform.scale(
                original_player_image, (int(player.width), int(player.height))
            )
            reset_player_visual_state(state, action="idle")

            player_animations = scale_animation_set(
                base_player_animations,
                (int(player.width), int(player.height))
            )

    elif state["game_state"] == g.STATE_BAR:
        update_bar(state, keys, player)
        update_player_animation(state, player_animations)
        current_player_frame = get_current_player_frame(
            state, player_animations, player_image
        )

        draw_bar(
            screen,
            bar,
            current_player_frame,
            player,
            character_rect,
            state,
            character_speech,
        )

        if keys[pygame.K_b]:
            player_image = leave_bar(state, player, door_rect, original_player_image)

            player_animations = scale_animation_set(
                base_player_animations,
                (int(player.width), int(player.height))
            )

    elif state["game_state"] == g.STATE_MENU:
        reset_player_visual_state(state, action="idle")
        draw_menu(screen, state)

    pygame.display.flip()
    clock.tick(g.FPS)

pygame.quit()
sys.exit()