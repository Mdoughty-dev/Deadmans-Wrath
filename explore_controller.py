import pygame
import sys
import globals as g
from battle_controller import start_battle
from player_visuals import reset_player_visual_state


def update_explore(state, keys, player, background):
    visual = state["player_visual_state"]
    moving = False

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= g.player_speed
        visual["action"] = "walk"
        visual["facing"] = "left"
        moving = True

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += g.player_speed
        visual["action"] = "walk"
        visual["facing"] = "right"
        moving = True

    if not moving:
        visual["action"] = "idle"

    state["camera_x"] = max(
        0,
        min(player.x - g.WIDTH // 2, background.get_width() - g.WIDTH),
    )


def draw_explore(screen, state, background, enemy_image, player_image, player, enemy, door_rect):
    camera_x = state["camera_x"]

    screen.blit(background, (-camera_x, 0))
    screen.blit(enemy_image, (enemy.x - camera_x, enemy.y))

    door_surface = pygame.Surface((door_rect.width, door_rect.height), pygame.SRCALPHA)
    door_surface.fill((255, 255, 255, 80))
    screen.blit(door_surface, (door_rect.x - camera_x, door_rect.y))

    screen.blit(player_image, (player.x - camera_x, player.y))


def handle_explore_keys(
    state,
    keys,
    screen,
    enemy,
    player,
    door_rect,
    original_player_image,
    creeper_image,
    player_image,
    enemy_image,
):
    if keys[pygame.K_m]:
        state["game_state"] = g.STATE_MENU
        reset_player_visual_state(state, action="idle")

    if player.colliderect(enemy):
        camera_x = state["camera_x"]

        pygame.draw.rect(screen, g.DARK_BLUE, (enemy.x - camera_x, enemy.y - 200, 700, 150))
        pygame.draw.rect(screen, g.WHITE, (enemy.x - camera_x, enemy.y - 200, 700, 150), 4)
        threat = g.font.render("What you looking at punk!", True, g.WHITE)
        screen.blit(threat, ((enemy.x - camera_x) + 30, enemy.y - 145))
        pygame.display.flip()

        pause_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - pause_start < 1000:
            for pause_event in pygame.event.get():
                if pause_event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        reset_player_visual_state(state, action="idle")
        player_image, enemy_image = start_battle(
            state, player, enemy, original_player_image, creeper_image
        )

    if player.colliderect(door_rect) and keys[pygame.K_e]:
        state["game_state"] = g.STATE_BAR
        state["show_dialogue"] = False
        state["dialogue_tracker"] = 0
        player.x = 100
        player.y = 300
        player.width = player.width * 2
        player.height = player.height * 2
        player_image = pygame.transform.scale(
            original_player_image, (int(player.width), int(player.height))
        )
        reset_player_visual_state(state, action="idle")

    return player_image, enemy_image