import pygame
import sys
from loader import load_assets
import globals as g

pygame.init()

# Screen setup
screen = pygame.display.set_mode((g.WIDTH, g.HEIGHT))
pygame.display.set_caption("The Deformed")
clock = pygame.time.Clock()

# Load assets
assets = load_assets(g.WIDTH, g.HEIGHT)
background = assets["background"]
original_player_image = assets["character"]
creeper = assets["enemy"]
bar = assets["bar"]

# Player setup
player = pygame.Rect(600, (g.HEIGHT / 2) - (g.HEIGHT / 8), g.HEIGHT / 8, g.HEIGHT / 4)
player_image = pygame.transform.scale(original_player_image, (int(player.width), int(player.height)))

# Enemy setup
enemy = pygame.Rect(1800, (g.HEIGHT / 2) - (g.HEIGHT / 8), g.HEIGHT / 8, g.HEIGHT / 4)
enemy_image = pygame.transform.scale(creeper, (int(enemy.width), int(enemy.height)))

# Character
character = pygame.Rect(300, 200, 300, 300)

# Door setup
door_rect = pygame.Rect(1400, g.HEIGHT - 625, 80, 150)

# Dialogue
character_speech = ["hello", "how are you", "what do you want"]
dialogue_tracker = 0
show_dialogue = False

# Initialize game state
game_state = g.STATE_EXPLORE

# Battle variables
player_hp = g.player_hp
player_max_hp = g.player_max_hp
player_mp = g.player_mp
player_max_mp = g.player_max_mp
player_atb = g.player_atb
battle_menu_index = g.battle_menu_index
magic_index = g.magic_index
player_turn = g.player_turn
in_magic_menu = g.in_magic_menu
battle_log = g.battle_log

enemy_hp = g.enemy_hp
enemy_max_hp = g.enemy_max_hp
enemy_atb = g.enemy_atb
enemy_turn = g.enemy_turn
enemy_attack_index = g.enemy_attack_index

camera_x = g.camera_x


def draw_battle_ui():
    box_width = 300
    box_height = 200
    box_x = 10
    box_y = g.HEIGHT - box_height - 170

    pygame.draw.rect(screen, g.DARK_BLUE, (box_x + 300, box_y, box_width, box_height))
    pygame.draw.rect(screen, g.WHITE, (box_x + 300, box_y, box_width, box_height), 4)

    options = g.magic_options if in_magic_menu else g.menu_options
    selected_index = magic_index if in_magic_menu else battle_menu_index

    for i, option in enumerate(options):
        color = g.RED if i == selected_index else g.WHITE
        text = g.font.render(option, True, color)
        screen.blit(text, (box_x + 320, box_y + i * 55))

    info_box_height = 160
    info_box_y = box_y

    pygame.draw.rect(screen, g.DARK_BLUE, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, g.WHITE, (box_x, box_y, box_width, box_height), 4)

    pygame.draw.rect(screen, g.DARK_BLUE, (g.WIDTH - 620, box_y, 500, info_box_height))
    pygame.draw.rect(screen, g.RED, (g.WIDTH - 620, box_y, 500, info_box_height), 4)

    name_text = g.font.render(g.player_name, True, g.WHITE)
    hp_text = g.font.render(f"HP: {player_hp}/{player_max_hp}", True, g.WHITE)
    mp_text = g.font.render(f"MP: {player_mp}/{player_max_mp}", True, g.WHITE)
    enemy_hp_text = g.font.render(f"Enemy HP: {enemy_hp}/{enemy_max_hp}", True, g.WHITE)

    screen.blit(name_text, (box_x + 20, info_box_y + 10))
    screen.blit(hp_text, (box_x + 20, info_box_y + 60))
    screen.blit(mp_text, (box_x + 20, info_box_y + 100))
    screen.blit(enemy_hp_text, (g.WIDTH - 600, info_box_y + 60))

    atb_bar_width = box_width - 40
    atb_bar_height = 10
    atb_x = box_x + 20
    atb_y = info_box_y + info_box_height - 20

    pygame.draw.rect(screen, g.WHITE, (atb_x, atb_y, atb_bar_width, atb_bar_height), 2)
    atb_fill = int((player_atb / g.atb_max) * (atb_bar_width - 4))
    pygame.draw.rect(screen, (50, 100, 255), (atb_x + 2, atb_y + 2, atb_fill, atb_bar_height - 4))

    log_text = g.font.render(battle_log, True, g.WHITE)
    screen.blit(log_text, (g.WIDTH // 2 - log_text.get_width() // 2, 30))
##MENU UI 
def draw_menu():
     screen.fill(g.BLACK)   
     pygame.draw.rect(screen, g.WHITE, (0, 0, g.WIDTH / 2, g.HEIGHT), 4)
     pygame.draw.rect(screen, g.WHITE, (0, 0, g.WIDTH / 2, 150), 4)
     party = g.font.render("PARTY", True, g.WHITE)
     screen.blit(party, (400, 75))
     pygame.draw.rect(screen, g.WHITE, (g.WIDTH / 2, 0, g.WIDTH / 2, g.HEIGHT), 4)
     pygame.draw.rect(screen, g.WHITE, (g.WIDTH / 2, 0, g.WIDTH / 2, 150), 4)
     notes = g.font.render("NOTES", True, g.WHITE)
     screen.blit(notes, (g.WIDTH - 550, 75))
     profile_pic_width = 200
     profile_pic_height = 200
     pygame.draw.rect(screen, g.WHITE, (100, 250, profile_pic_width, profile_pic_height))

# Main loop
running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Battle input
        if game_state == g.STATE_BATTLE and player_turn and event.type == pygame.KEYDOWN:
            if in_magic_menu:
                if event.key == pygame.K_DOWN:
                    magic_index = (magic_index + 1) % len(g.magic_options)
                elif event.key == pygame.K_UP:
                    magic_index = (magic_index - 1) % len(g.magic_options)
                elif event.key == pygame.K_RETURN:
                    spell = g.magic_options[magic_index]
                    if spell == "Hex" and player_mp >= 10:
                        player_mp -= 10
                        enemy_hp -= 50
                        battle_log = f"{g.player_name} casts Hex for 50 damage!"
                    elif spell == "Cure" and player_mp >= 5:
                        player_mp -= 5
                        player_hp = min(player_max_hp, player_hp + 40)
                        battle_log = f"{g.player_name} casts Cure and heals 40 HP!"
                    player_atb = 0
                    player_turn = False
                    in_magic_menu = False
                elif event.key == pygame.K_ESCAPE:
                    in_magic_menu = False
            else:
                if event.key == pygame.K_DOWN:
                    battle_menu_index = (battle_menu_index + 1) % len(g.menu_options)
                elif event.key == pygame.K_UP:
                    battle_menu_index = (battle_menu_index - 1) % len(g.menu_options)
                elif event.key == pygame.K_RETURN:
                    action = g.menu_options[battle_menu_index]
                    if action == "Attack":
                        enemy_hp -= 20
                        battle_log = f"{g.player_name} attacks for 20 damage!"
                    elif action == "Magic":
                        in_magic_menu = True
                        continue
                    player_atb = 0
                    player_turn = False

        # Bar dialogue input
        if game_state == g.STATE_BAR and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and player.colliderect(character):
                if not show_dialogue:
                    show_dialogue = True
                    dialogue_tracker = 0
                else:
                    dialogue_tracker += 1
                    if dialogue_tracker >= len(character_speech):
                        dialogue_tracker = 0
                        show_dialogue = False

    if game_state == g.STATE_EXPLORE:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= g.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += g.player_speed

        camera_x = max(0, min(player.x - g.WIDTH // 2, background.get_width() - g.WIDTH))
        screen.blit(background, (-camera_x, 0))
        screen.blit(enemy_image, (enemy.x - camera_x, enemy.y))

        door_surface = pygame.Surface((door_rect.width, door_rect.height), pygame.SRCALPHA)
        door_surface.fill((255, 255, 255, 80))
        screen.blit(door_surface, (door_rect.x - camera_x, door_rect.y))

        screen.blit(player_image, (player.x - camera_x, player.y))

        if keys[pygame.K_m]:
            game_state = g.STATE_MENU

        if player.colliderect(enemy):
            game_state = g.STATE_BATTLE
            player_atb = 0
            enemy_atb = 0
            player_turn = False
            enemy_turn = False
            player.x = 450
            player.y = 175
            enemy.y = 175
            enemy.x -= 150
            player.width = player.width * 2
            player.height = player.height * 2
            player_image = pygame.transform.scale(original_player_image,(int(player.width),int(player.height)))
            enemy.width = enemy.width * 2
            enemy.height = enemy.height * 2
            enemy_image = pygame.transform.scale(creeper,(int(enemy.width), int(enemy.height)))

        if player.colliderect(door_rect) and keys[pygame.K_e]:
            game_state = g.STATE_BAR
            show_dialogue = False
            dialogue_tracker = 0
            player.x = 100
            player.y = 300
            player.width = player.width * 2
            player.height = player.height * 2
            player_image = pygame.transform.scale(
                original_player_image, (int(player.width), int(player.height))
            )

    elif game_state == g.STATE_BATTLE:
        screen.fill(g.BLACK)
        screen.blit(enemy_image, (g.WIDTH - enemy.width - 100, enemy.y))
        screen.blit(player_image, (250, player.y))

        if not player_turn:
            player_atb += 0.5
            if player_atb >= g.atb_max:
                player_atb = g.atb_max
                player_turn = True

        if not player_turn and not enemy_turn:
            enemy_atb += 0.5
            battle_log = ""
            if enemy_atb >= g.atb_max:
                enemy_turn = True

        if enemy_turn and not player_turn:
            attack = g.enemy_attack_cycle[enemy_attack_index]
            damage = 25 if attack == "Knife Stab" else 35
            player_hp -= damage
            battle_log = f"Enemy uses {attack} for {damage} damage!"
            enemy_attack_index = (enemy_attack_index + 1) % len(g.enemy_attack_cycle)
            enemy_atb = 0
            enemy_turn = False

        draw_battle_ui()

        if player_hp <= 0:
            battle_log = "Game Over!"
            print("Game Over!")
            running = False

        if enemy_hp <= 0:
            battle_log = "Enemy defeated!"
            print("Enemy defeated!")
            game_state = g.STATE_EXPLORE
            enemy.x = 10000
            player.y = 450
            player.x = 1800
            player.width = player.width / 2
            player.height = player.height / 2
            player_image = pygame.transform.scale(
                original_player_image, (int(player.width), int(player.height))
            )



        if keys[pygame.K_r]:
            game_state = g.STATE_EXPLORE
            player.x = 600

    elif game_state == g.STATE_BAR:
        screen.fill((30, 15, 15))
        screen.blit(bar, (0, 0))

        character_surface = pygame.Surface((character.width, character.height), pygame.SRCALPHA)
        character_surface.fill((0, 0, 0,0))
        screen.blit(character_surface, (character.x, character.y))

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= g.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += g.player_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= g.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += g.player_speed

        if player.colliderect(character) and show_dialogue:
            pygame.draw.rect(screen, g.DARK_BLUE, (character.x, character.y - 50, 500, 100))
            pygame.draw.rect(screen, g.WHITE, (character.x, character.y - 50, 500, 100), 4)

            character_text = g.font.render(character_speech[dialogue_tracker], True, g.WHITE)
            screen.blit(character_text, (character.x + 20, character.y - 30))

        screen.blit(player_image, (player.x, player.y))

        if keys[pygame.K_b]:
            game_state = g.STATE_EXPLORE
            show_dialogue = False
            dialogue_tracker = 0
            player.x = door_rect.x + 100
            player.y = 400
            player.width = player.width / 2
            player.height = player.height / 2
            player_image = pygame.transform.scale(
                original_player_image, (int(player.width), int(player.height))
            )
    if game_state == g.STATE_MENU:
        draw_menu();
        if keys[pygame.K_b]:
            game_state = g.STATE_EXPLORE

    pygame.display.flip()
    clock.tick(g.FPS)

pygame.quit()
sys.exit()
