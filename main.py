import pygame
import time
from framework.constants import *
from framework.framework import *
from framework.images import *
from framework.player import Player
from framework.bullet import Bullet
import random 
import numpy as np
import sys
import os
pygame.init()

display = pygame.Surface((200, 155))
clock = pygame.time.Clock()

crosshair_img = pygame.image.load(os.path.join("assets", "images", "crosshair.png")).convert()
crosshair_img.set_colorkey((0,0,0))

player = Player(70, 150, 2)
prev_time = time.time()
scroll = [0, 0]
BLOCK_DICT = {
    "grass_left": block_left,
    "grass_right": block_right,
    "grass": grass_block,
    "grass_side_left": block_side_left,
    "grass_side_right": block_side_right,
    "dirt": dirt_block,
    "torch": torch,
    "enemy": foliage1,
    "foliage2": foliage2

}
health = 5
grass = []
bullets = []
torches = []
enemies = []
decorations = []

pygame.mixer.music.load("assets/music/music.wav")
pygame.mixer.music.play(-1)

jump_sound = pygame.mixer.Sound("assets/sound effects/jump.wav")
jump_sound.set_volume(0.1)

shoot_sound = pygame.mixer.Sound("assets/sound effects/laserShoot.wav")
shoot_sound.set_volume(0.5)

explosion_sound = pygame.mixer.Sound("assets/sound effects/explosion.wav")
explosion_sound.set_volume(0.3)

hit_sound = pygame.mixer.Sound("assets/sound effects/hit.wav")
hit_sound.set_volume(0.3)

dead = False
has_played_death_animation = False

special_tiles = [["torch", torches], ["foliage2", decorations]]

enemy_count = 0

levels = ["tutorial", "map", "map1", "map2", "map3", "map4", "map5", "map6", "map7", "end"]
level_index = 0
tiles = load_map(f"assets/map/{levels[level_index]}.txt")

for tile in tiles:
      for t in special_tiles:
            if t[0] == tile[2]:
                  t[1].append(tile)
                  tiles.remove(tile)

      if tile[2] == "enemy":
            enemy_count += 1
            enemies.append([tile[0], tile[1], tile[2], random.randrange(0, 30)])
            tiles.remove(tile)


font = pygame.font.SysFont("Arial", 20)
def rotate(image, rotation):
      return pygame.transform.rotate(image, rotation)

bg_sqaures = []

small_squares = []
global_time = 0

leaves = []

screen_shake = 0

kills = 0

explosion_effects = []

light_mask_full = pygame.transform.scale(light_mask_base, (400, 300))
light_mask_full.blit(light_mask_full, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

enemy_bullets = []
enemy_bullet_pattern = [[0, 1], [0, -1], [1, 0], [-1, 0], [.5, .5], [.5, -.5], [-.5, .5], [-.5, -.5]]

enemy_bullet_cooldown = 0

def glow(surf, host, pos, radius, offset=0):
    if host:
        timing_offset = (hash(host) / 1000) % 1
        timing_offset += 1
    else:
        timing_offset = 0
    glow_width = abs(math.sin(global_time+offset)*25) + radius *2

    glow_img = light_mask_base
    surf.blit(pygame.transform.scale(glow_img, (glow_width, glow_width)), (pos[0]-glow_width/2, pos[1]-glow_width/2), special_flags=pygame.BLEND_RGBA_ADD)

torch_effects = []
particles = []
explosions = []
pygame.display.set_caption("Planyt")
pygame.display.set_icon(pygame.image.load("icon.ico"))
radius = 5
while True:
      pygame.mouse.set_visible(False)
      mx, my = pygame.mouse.get_pos()
      scroll[0] += (player.player_rect.x-scroll[0]-(150//1.5)+mx/50)/10
      scroll[1] += (player.player_rect.y-scroll[1]-(75//1.5)+my/50)/10
      display.fill((77,77,126))
      dt = 1/60

      global_time += dt

      light_surf = display.copy()
      light_surf.fill((5, 15, 35))


      mouse_x, mouse_y = pygame.mouse.get_pos()
      mouse_x, mouse_y = mouse_x/4.5, mouse_y/4.5



      rand_event = random.randrange(0, 20)
      if rand_event == 3:
            for i in range(1):
                  bg_sqaures.append([random.randrange(0, 800), 400, 0])
                  
      for square in bg_sqaures:
            square[1] -= 1
            square[2] += 1
            if square[1] < -100:
                  bg_sqaures.remove(square)
            display.blit(rotate(pygame.image.load("assets/images/square.png"), square[2]), (square[0]-scroll[0], square[1]-scroll[1]))

      for img in grass:
            if pygame.Rect(player.player_rect.x-scroll[0], player.player_rect.y-scroll[1], player.player_rect.width, player.player_rect.height).colliderect(
                  pygame.Rect(img[1]-scroll[0], img[2]-scroll[1], 16, 16)
            ):
                  pass
            else:
                  img[3] += .1
            display.blit(rotate(img[0], np.sin(img[3])*10), (img[1]-scroll[0], img[2]-scroll[1]))
      for t in torches:
            display.blit(torch, (int(t[0])-scroll[0], int(t[1])-scroll[1]-350))
            event = random.randrange(0,5)
            if event == 3:
                  torch_effects.append([int(t[0])+random.randrange(0, 10), int(t[1])-345, global_time*random.random(), .2, 3, random.randrange(0, 100)])

      for event in pygame.event.get():
            if event.type == pygame.QUIT:
                  pygame.quit()
                  sys.exit()
            if event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_SPACE:
                        jump_sound.play()
                        if player.air_timer < 6:
                              player.vertical_momentum = -4

            if event.type == pygame.MOUSEBUTTONDOWN:
                  if event.button == 1:
                        shoot_sound.play()
                        screen_shake += 2
                        rel_x, rel_y = mouse_x - (player.player_rect.x-scroll[0]), mouse_y - (player.player_rect.y-scroll[1])
                        bullets.append(Bullet(player.player_rect.x-scroll[0]+4, player.player_rect.y-scroll[1]+4, mouse_x, mouse_y, rel_x, rel_y))
      for b in range(len(bullets)):
            try:
                  bullet = bullets[b]
                  for tile in tiles:
                        if pygame.Rect(bullet.x, bullet.y, 4, 4).colliderect(pygame.Rect(int(tile[0])-scroll[0], int(tile[1])-scroll[1]-350, 16, 16)):
                              for i in range(15):
                                    particles.append([int(tile[0]), int(tile[1])-350, random.randrange(-15, 15), random.randrange(-3*5, 3*5), random.randrange(0, 360), 100])
                              screen_shake += 4

                              bullets.remove(bullet)

                  for enemy in enemies:
                        rect = pygame.Rect(int(enemy[0])-scroll[0], int(enemy[1])-scroll[1]-350, 16, 16)
                        if pygame.Rect(bullet.x, bullet.y, 4, 4).colliderect(rect):
                              for i in range(100):
                                    explosions.append([int(enemy[0]), int(enemy[1])-350+random.randrange(-7, 7), random.randrange(-4, 4),random.randrange(-2, 7), 1, (242, 211, 171), False, .2, 100])
                              explosion_sound.play()
                              for i in range(15):
                                    particles.append([int(tile[0]), int(tile[1])-350, random.randrange(-15, 15), random.randrange(-3*5, 3*5), random.randrange(0, 360), 1])
                              screen_shake += 8
                              kills += 1
                              enemies.remove(enemy)
                              bullets.remove(bullet)

            except:
                  pass
            bullet.main(display)


      for index, enemy in enumerate(enemies):
            display.blit(BLOCK_DICT[enemy[2]], (int(enemy[0])-scroll[0], int(enemy[1])-scroll[1]-350))

            if enemy[3] == 0:
                  x = int(enemy[0])-scroll[0]
                  y = int(enemy[1])-scroll[1]-350
                  px = player.player_rect.x-scroll[0]+random.randrange(-30, 30)
                  py = player.player_rect.y-scroll[1]+random.randrange(-30, 30)


                  angle = math.atan2(y-py, x-px)
                  x_vel = math.cos(angle) * 1
                  y_vel = math.sin(angle) * 1


                  enemy_bullets.append([int(enemy[0])+5, int(enemy[1])-348, [x_vel, y_vel], 400])
                  enemy[3] = random.randrange(50, 80)

            else:
                  enemy[3] -= 1

      if enemy_bullet_cooldown > 0:
            enemy_bullet_cooldown -= 1


      glow(light_surf, player, (player.player_rect.x-scroll[0], player.player_rect.y-scroll[1]), 130)
      tile_rects = render_tiles(display, scroll, tiles, [player.player_rect.x-scroll[0], player.player_rect.y-scroll[1]], BLOCK_DICT)
      
      for effect in torch_effects:
            effect[1] -= effect[3]
            glow(light_surf, None, (effect[0]-scroll[0]+math.sin(effect[2])*2, effect[1]-scroll[1]), 2, effect[5])
            effect[2] += .1
            effect[3] -= .0005
            effect[4] -= .02
            pygame.draw.circle(display, (255, 180, 122), (effect[0]-scroll[0]+math.sin(effect[2])*2, effect[1]-scroll[1]+effect[3]), effect[4])
            if effect[4] <= 0:
                  torch_effects.remove(effect)

      for decoration in decorations:
            display.blit(BLOCK_DICT[decoration[2]], (int(decoration[0])-scroll[0], int(decoration[1])-scroll[1]-350))
      event = random.randrange(0, 30)
      if event == 3:
            leaves.append([random.randrange(0, 300), 0])

      for leaf in leaves:
            pygame.draw.circle(display, (242, 211, 171), (leaf[0]-scroll[0], leaf[1]-scroll[1]), 1)
            leaf[1] += 1
            leaf[0] += np.sin(global_time)

            if leaf[1] > 200:
                  leaves.remove(leaf)

      for particle in particles:
            x_vel = math.cos(particle[4])
            y_vel = math.sin(particle[4])
            particle[5] -= 1
            particle[0] -= x_vel*2
            particle[1] -= y_vel*2
            display.blit(pygame.transform.rotate(spark_img, particle[4]), (particle[0]-scroll[0], particle[1]-scroll[1]))
            if particle[5] <= 0:
                  particles.remove(particle)
      for bullet in enemy_bullets:
            if bullet[3] <= 0:
                  enemy_bullets.remove(bullet)
            bullet[0] -= bullet[2][0]
            bullet[1] -= bullet[2][1]
            bullet[3] -= 1
            glow(light_surf, None, (bullet[0]-scroll[0], bullet[1]-scroll[1]), 2, 2)

            if pygame.Rect(player.player_rect.x-scroll[0], player.player_rect.y-scroll[1], 16, 16).colliderect(pygame.Rect(bullet[0]-scroll[0]-8, bullet[1]-scroll[1]-8, 4, 4)):
                  if health > 0:
                        health -= 1
                  hit_sound.play()
                  enemy_bullets.remove(bullet)
                  screen_shake += 5
            
            display.blit(enemy_bullet_img, (bullet[0]-scroll[0]-8, bullet[1]-scroll[1]-8))

      for eff in explosion_effects:
            eff[2] -= 1
            if eff[2] <= 0:
                  explosion_effects.remove(eff)
            pygame.draw.circle(display, (39, 39, 68), (eff[0]-scroll[0],eff[1]-scroll[1]), 1)
      for part in explosions:
            if part[7] <= 0:
                  explosions.remove(part)
            part[1] -= part[3]*random.random()
            if part[3] > -10:
                  part[3] -= .3
            part[0] += part[2]*random.random()
            part[4] += .01
            part[7] -= .005
            if part[6] is False:
                  explosion_effects.append([part[0], part[1], 10])

            pygame.draw.circle(display, part[5], (part[0]-scroll[0], part[1]-scroll[1]), part[4])

      if level_index == 0:
            render_text(display, "shoot", (70, 150+math.sin(global_time*5)*2), scroll)
            display.blit(foliage1, (110-scroll[0], 150+math.sin(global_time*5)*2-scroll[1]))

      if level_index == 9:
            render_text(display, "thanks for playing", (130, 150+math.sin(global_time*5)*2), scroll)

      if screen_shake:
            scroll[0] += random.randint(0, 8) - 4
            scroll[1] += random.randint(0, 8) - 4

      if screen_shake > 0:
            screen_shake -= 1

      display.blit(light_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
      render_text(display, f"{kills}/{enemy_count}", (20, 10+math.sin(global_time*5)*2), [0, 0])
      display.blit(foliage1, (5, 5+math.sin(global_time*5)*2))

      render_text(display, f"{health}/5", (20, 30+math.sin(global_time*5)*2), [0, 0])
      display.blit(heart_img, (5, 30+math.sin(global_time*5)*2))
      display.blit(crosshair_img, (mouse_x, mouse_y))
      if health <= 0:
            dead = True

      if dead:
            if not has_played_death_animation:
                  for i in range(100):
                        explosions.append([player.player_rect.x, player.player_rect.y+random.randrange(-7, 7), random.randrange(-4, 4),random.randrange(-2, 7), 1, (242, 211, 171), False, .2, 100])
                  has_played_death_animation = True
                  screen_shake += 4
            pygame.draw.circle(display, (0, 0, 0), (200//2, 155//2), radius)
            radius += radius/25
            if radius >= 350:
                  decorations = []
                  torches = []
                  torch_effects = []
                  special_tiles = [["torch", torches], ["foliage2", decorations]]
                  health = 5
                  enemies = []
                  enemy_bullets = []
                  dead = False
                  has_played_death_animation = False
                  level_index = 0
                  if level_index == 0:
                        player = Player(70, 150, 2)
                  else:
                        player = Player(180, 200, 2)
                  radius = 5
                  enemy_count = 0
                  kills = 0
                  tiles = load_map(f"assets/map/{levels[level_index]}.txt")

                  for tile in tiles:
                        for t in special_tiles:
                              if t[0] == tile[2]:
                                    t[1].append(tile)
                                    tiles.remove(tile)

                        if tile[2] == "enemy":
                              enemy_count += 1
                              enemies.append([tile[0], tile[1], tile[2], random.randrange(0, 30)])
                              tiles.remove(tile)

      else:
            player.main(display, dt, tile_rects, scroll)

      if player.player_rect.y > 300:
            pygame.draw.circle(display, (0, 0, 0), (200//2, 155//2), radius)
            radius += radius/25
            if radius >= 350:
                  decorations = []
                  torches = []
                  torch_effects = []
                  special_tiles = [["torch", torches], ["foliage2", decorations]]
                  health = 5
                  enemies = []
                  enemy_bullets = []
                  dead = False
                  has_played_death_animation = False
                  level_index = 0
                  if level_index == 0:
                        player = Player(70, 150, 2)
                  else:
                        player = Player(180, 200, 2)
                  radius = 5
                  enemy_count = 0
                  kills = 0
                  tiles = load_map(f"assets/map/{levels[level_index]}.txt")

                  for tile in tiles:
                        for t in special_tiles:
                              if t[0] == tile[2]:
                                    t[1].append(tile)
                                    tiles.remove(tile)

                        if tile[2] == "enemy":
                              enemy_count += 1
                              enemies.append([tile[0], tile[1], tile[2], random.randrange(0, 30)])
                              tiles.remove(tile)
                              
      if kills == enemy_count and level_index != 9:
            pygame.draw.circle(display, (0, 0, 0), (200//2, 155//2), radius)
            radius += radius/25
            if radius >= 300:
                  decorations = []
                  torches = []
                  torch_effects = []
                  health = 5
                  special_tiles = [["torch", torches], ["foliage2", decorations]]
                  enemies = []
                  dead = False
                  has_played_death_animation = False
                  player = Player(180, 200, 2)
                  radius = 5
                  enemy_count = 0
                  kills = 0
                  level_index += 1
                  tiles = load_map(f"assets/map/{levels[level_index]}.txt")

                  for tile in tiles:
                        for t in special_tiles:
                              if t[0] == tile[2]:
                                    t[1].append(tile)
                                    tiles.remove(tile)

                        if tile[2] == "enemy":
                              enemy_count += 1
                              enemies.append([tile[0], tile[1], tile[2], random.randrange(0, 30)])
                              tiles.remove(tile)
      
      SCREEN.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
      pygame.display.flip() 
      CLOCK.tick(FPS)
