import pygame
import globals as g
from player_visuals import reset_player_visual_state, apply_depth_scaling


def handle_bar_input(event, state, player, character_speech, character_rect):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_e and player.colliderect(character_rect):
            if not state["show_dialogue"]:
                state["show_dialogue"] = True
                state["dialogue_tracker"] = 0
            else:
                state["dialogue_tracker"] += 1
                if state["dialogue_tracker"] >= len(character_speech):
                    state["dialogue_tracker"] = 0
                    state["show_dialogue"] = False


def update_bar(state, keys, player, base_width, base_height):
    visual = state["player_visual_state"]
    moving = False

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.y -= g.player_speed
        visual["action"] = "walk"
        visual["facing"] = "up"
        moving = True

    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.y += g.player_speed
        visual["action"] = "walk"
        visual["facing"] = "down"
        moving = True

    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= g.player_speed
        visual["action"] = "walk"
        visual["facing"] = "left"
        moving = True

    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += g.player_speed
        visual["action"] = "walk"
        visual["facing"] = "right"
        moving = True
    
    apply_depth_scaling(player, base_width, base_height)

    if not moving:
        visual["action"] = "idle"



def draw_bar(screen, bar_image, player_image, player, character_rect, state, character_speech):
    screen.fill((30, 15, 15))
    screen.blit(bar_image, (0, 0))

    character_surface = pygame.Surface((character_rect.width, character_rect.height), pygame.SRCALPHA)
    character_surface.fill((0, 0, 0, 0))
    screen.blit(character_surface, (character_rect.x, character_rect.y))

    if player.colliderect(character_rect) and state["show_dialogue"]:
        pygame.draw.rect(screen, g.DARK_BLUE, (character_rect.x, character_rect.y - 50, 500, 100))
        pygame.draw.rect(screen, g.WHITE, (character_rect.x, character_rect.y - 50, 500, 100), 4)

        character_text = g.font.render(
            character_speech[state["dialogue_tracker"]], True, g.WHITE
        )
        screen.blit(character_text, (character_rect.x + 20, character_rect.y - 30))

    screen.blit(player_image, (player.x, player.y))


def leave_bar(state, player, door_rect, original_player_image):
    state["game_state"] = g.STATE_EXPLORE
    state["show_dialogue"] = False
    state["dialogue_tracker"] = 0
    player.x = door_rect.x + 100
    player.y = 400
    player.width = g.HEIGHT / 8
    player.height = g.HEIGHT / 4

    reset_player_visual_state(state, action="idle")

    return pygame.transform.scale(
        original_player_image, (int(player.width), int(player.height))
    )