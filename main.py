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

display_info = pygame.display.Info()
screen = pygame.display.set_mode(
    (display_info.current_w, display_info.current_h),
    pygame.FULLSCREEN
)
pygame.display.set_caption("The Deformed")
clock = pygame.time.Clock()

game_surface = pygame.Surface((g.WIDTH, g.HEIGHT))

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

explore_base_width = int(g.HEIGHT / 8)
explore_base_height = int(g.HEIGHT / 4)

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
        "animation_speed": 2,
    },
    "attack_motion": {
        "active": False,
        "phase": "forward",
        "timer": 0,
        "duration": 8,
        "distance": 80,
        "start_x": 0,
        "damage_applied": False,
        "return_to_idle": False,
    },
    "hit_pause": 0,
    "screen_shake": {
        "timer": 0,
        "strength": 0,
    },
    "spell_projectile": {
    "active": False,
    "spell_name": "",
    "damage": 0,
    "color": (255, 120, 40),
    "radius": 18,
    "x": 0,
    "y": 0,
    "target_x": 0,
    "target_y": 0,
    "speed": 24,
    "damage_applied": False,
    },
}

player_animations = scale_animation_set(
    base_player_animations,
    (int(player.width), int(player.height))
)


def present_scaled():
    real_width, real_height = screen.get_size()

    scaled_surface = pygame.transform.smoothscale(
        game_surface, (real_width, real_height)
    )

    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()


running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()

        if state["game_state"] == g.STATE_BATTLE:
            handle_battle_input(event, state, player, enemy)

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

            if event.key == pygame.K_b:
                state["game_state"] = g.STATE_EXPLORE
                reset_player_visual_state(state, action="idle")

    game_surface.fill(g.BLACK)

    if state["game_state"] == g.STATE_EXPLORE:
        update_explore(state, keys, player, background, explore_base_width, explore_base_height)
        update_player_animation(state, player_animations)
        current_player_frame = get_current_player_frame(
            state, player_animations, player_image
        )

        draw_explore(
            game_surface,
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
            game_surface,
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
        update_battle(state, player, enemy)
        target_enemy_x = g.WIDTH - enemy.width - 100
        if enemy.x > target_enemy_x:
            enemy.x -= 2
            if enemy.x < target_enemy_x:
                enemy.x = target_enemy_x

        draw_battle(game_surface, state, player_image, enemy_image, player, enemy)

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
        update_bar(state, keys, player,explore_base_width, explore_base_height)
        update_player_animation(state, player_animations)
        current_player_frame = get_current_player_frame(
            state, player_animations, player_image
        )

        draw_bar(
            game_surface,
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
        draw_menu(game_surface, state)
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()
        
    present_scaled()
    clock.tick(g.FPS)

pygame.quit()
sys.exit()