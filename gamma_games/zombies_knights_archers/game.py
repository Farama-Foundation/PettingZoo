#!usr/bin/env python3

# Importing Libraries
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import sys
sys.dont_write_bytecode = True
import pygame
import random
import pygame.gfxdraw
from src.players import Knight, Archer
from src.zombie import Zombie
from src.weapons import Arrow, Sword
from src.variables import *

class Game():
    def __init__(self):
        pass
    # Game Elements: Green - Zombie, Red - Archer, Blue - Knight, Black - Arrow, Gray - Sword

    # Controls the Spawn Rate of Weapons
    def check_weapon_spawn(self, sword_spawn_rate, arrow_spawn_rate):
        if sword_spawn_rate > 0:
            sword_spawn_rate += 1
        if sword_spawn_rate > 3:
            sword_spawn_rate = 0

        if arrow_spawn_rate > 0:
            arrow_spawn_rate += 1
        if arrow_spawn_rate > 3:
            arrow_spawn_rate = 0
        return sword_spawn_rate, arrow_spawn_rate

    # Spawn New Players
    class spawnPlayers(pygame.sprite.Sprite):
        def __init__(self, event, knight_player_num, archer_player_num, knight_list, archer_list, all_sprites, knight_dict, archer_dict):
            super().__init__()
            self.event = event
            self.knight_player_num = knight_player_num
            self.archer_player_num = archer_player_num
            self.knight_dict = knight_dict
            self.archer_dict = archer_dict
            self.knight_list = knight_list
            self.archer_list = archer_list
            self.all_sprites = all_sprites

        # Spawn New Knight
        def spawnKnight(self):
            if self.event.key == pygame.K_m:
                self.knight_player_num += 1
                self.knight_dict['knight{0}'.format(self.knight_player_num)] = Knight(blue_trigon, OBJ_RADIUS)
                self.knight_list.add(self.knight_dict['knight{0}'.format(self.knight_player_num)])
                self.all_sprites.add(self.knight_dict['knight{0}'.format(self.knight_player_num)])
            return self.knight_player_num, self.knight_list, self.all_sprites, self.knight_dict

        # Spawn New Archer
        def spawnArcher(self):
            if self.event.key == pygame.K_x:
                self.archer_player_num += 1
                self.archer_dict['archer{0}'.format(self.archer_player_num)] = Archer(red_trigon, OBJ_RADIUS)
                self.archer_list.add(self.archer_dict['archer{0}'.format(self.archer_player_num)])
                self.all_sprites.add(self.archer_dict['archer{0}'.format(self.archer_player_num)])
            return self.archer_player_num, self.archer_list, self.all_sprites, self.archer_dict
                
    # Spawn New Weapons
    class spawnWeapons(pygame.sprite.Sprite):
        def __init__(self, event, sword_spawn_rate, arrow_spawn_rate, knight_killed, archer_killed,
                    knight_dict, archer_dict, knight_list, archer_list, knight_player_num, archer_player_num,
                    all_sprites, sword_dict, arrow_dict, sword_list, arrow_list):
            super().__init__()
            self.event = event
            self.sword_spawn_rate = sword_spawn_rate
            self.arrow_spawn_rate = arrow_spawn_rate
            self.knight_killed = knight_killed
            self.archer_killed = archer_killed
            self.knight_dict = knight_dict
            self.archer_dict = archer_dict
            self.knight_list = knight_list
            self.archer_list = archer_list
            self.knight_player_num = knight_player_num
            self.archer_player_num = archer_player_num
            self.all_sprites = all_sprites
            self.sword_dict = sword_dict
            self.arrow_dict = arrow_dict
            self.sword_list = sword_list
            self.arrow_list = arrow_list

        # Spawning Swords for Players
        def spawnSword(self):
            if (self.event.key == pygame.K_SEMICOLON and self.sword_spawn_rate == 0):
                if not sword_list:      # Sword List is Empty
                    if not self.knight_killed:
                        for i in range(0, self.knight_player_num + 1):
                            self.sword_dict['sword{0}'.format(i)] = Sword((self.knight_dict['knight{0}'.format(i)]), OBJ_RADIUS)
                            self.sword_list.add(self.sword_dict[('sword{0}'.format(i))])
                            self.all_sprites.add(self.sword_dict[('sword{0}'.format(i))])
                        self.sword_spawn_rate = 1
                        self.knight_killed = False
                    else:
                        for knight in self.knight_list:
                            temp = Sword(knight, OBJ_RADIUS)
                            self.sword_list.add(temp)
                            self.all_sprites.add(temp)
                        self.sword_spawn_rate = 1
            return self.sword_spawn_rate, self.knight_killed, self.knight_dict, self.knight_list, self.knight_player_num, self.all_sprites, self.sword_dict, self.sword_list

        # Spawning Arrows for Players
        def spawnArrow(self):
            if (self.event.key == pygame.K_f and self.arrow_spawn_rate == 0):
                if not self.archer_killed:
                    for i in range(0, self.archer_player_num + 1):
                        self.arrow_dict[('arrow{0}'.format(i))] = Arrow(self.archer_dict[('archer{0}'.format(i))], OBJ_RADIUS)
                        self.arrow_list.add(self.arrow_dict[('arrow{0}'.format(i))])
                        self.all_sprites.add(self.arrow_dict[('arrow{0}'.format(i))])
                    self.arrow_spawn_rate = 1
                    self.archer_killed = False   
                else:
                    for archer in self.archer_list:
                        temp = Arrow(archer, OBJ_RADIUS)
                        self.arrow_list.add(temp)
                        self.all_sprites.add(temp)
                    self.arrow_spawn_rate = 1
            return self.arrow_spawn_rate, self.archer_killed, self.archer_dict, self.archer_list, self.archer_player_num, self.all_sprites, self.arrow_dict, self.arrow_list

    # Stab the Sword
    def sword_stab(self, sword_list, all_sprites):
        try:
            for sword in sword_list:
                sword_active = sword.update()
                if not sword_active: # remove the sprite
                    sword_list.remove(sword)
                    all_sprites.remove(sword)
        except:
            pass
        return sword_list, all_sprites

    # Spawning Zombies at Random Location at every 100 iterations
    def spawn_zombie(self, zombie_spawn_rate, zombie_list, all_sprites):
        zombie_spawn_rate += 1
        zombie = Zombie(GREEN, circle, OBJ_RADIUS)

        if zombie_spawn_rate >= ZOMBIE_SPAWN:
            zombie.rect.x = random.randrange(WIDTH)
            zombie.rect.y = 5

            zombie_list.add(zombie)
            all_sprites.add(zombie)
            zombie_spawn_rate = 0
        return zombie_spawn_rate, zombie_list, all_sprites

    # Zombie Kills the Knight
    def zombie_knight(self, zombie_list, knight_list, all_sprites, knight_killed, sword_list, sword_killed):
        for zombie in zombie_list:
            zombie_knight_list = pygame.sprite.spritecollide(zombie, knight_list, True)

            for knight in zombie_knight_list:
                knight.alive = False
                knight_list.remove(knight)
                all_sprites.remove(knight)
                sword_killed = True
                knight_killed = True
        return zombie_list, knight_list, all_sprites, knight_killed, sword_list, sword_killed

    # Kill the Sword when Knight dies
    def kill_sword(self, sword_killed, sword_list, all_sprites):
        for sword in sword_list:
            if sword_killed == True:
                sword_list.remove(sword)
                all_sprites.remove(sword)
                sword_killed = False
        return sword_killed, sword_list, all_sprites

    # Zombie Kills the Archer
    def zombie_archer(self, zombie_list, archer_list, all_sprites, archer_killed):
        for zombie in zombie_list:
            zombie_archer_list = pygame.sprite.spritecollide(zombie, archer_list, True)

            for archer in zombie_archer_list:
                archer_list.remove(archer)
                all_sprites.remove(archer)
                archer_killed = True
        return zombie_list, archer_list, all_sprites, archer_killed

    # Zombie Kills the Sword
    def zombie_sword(self, zombie_list, sword_list, all_sprites, score):
        for sword in sword_list:
            zombie_sword_list = pygame.sprite.spritecollide(sword, zombie_list, True)

            # For each zombie hit, remove the sword and add to the score
            for zombie in zombie_sword_list:
                sword_list.remove(sword)
                all_sprites.remove(sword)
                zombie_list.remove(zombie)
                all_sprites.remove(zombie)
                score += 1
                print('Score: ', score)
        return zombie_list, sword_list, all_sprites, score

    # Zombie Kills the Arrow
    def zombie_arrow(self, zombie_list, arrow_list, all_sprites, score):
        for arrow in arrow_list:
            zombie_arrow_list = pygame.sprite.spritecollide(arrow, zombie_list, True)

            # For each zombie hit, remove the arrow, zombie and add to the score
            for zombie in zombie_arrow_list:
                arrow_list.remove(arrow)
                all_sprites.remove(arrow)
                zombie_list.remove(zombie)
                all_sprites.remove(zombie)
                score += 1
                print('Score: ', score)

            # Remove the arrow if it flies up off the screen
            if arrow.rect.y < 0:
                arrow_list.remove(arrow)
                all_sprites.remove(arrow)
        return zombie_list, arrow_list, all_sprites, score

    # Zombie reaches the End of the Screen
    def zombie_endscreen(self, run, zombie_list):
        for zombie in zombie_list:
            if zombie.rect.y > 690:
                print('*** GAME OVER - Zombie Reached the End ***')
                run = False
        return run

    # Zombie Kills all Players
    def zombie_all_players(self, knight_list, archer_list, run):
        if not knight_list and not archer_list:
            run = False
            print('*** GAME OVER - All Players are Dead ***')
        return run

    # Game Loop
    def step(self):
        while run:
            # Controls the Spawn Rate of Weapons
            sword_spawn_rate, arrow_spawn_rate = check_weapon_spawn(sword_spawn_rate, arrow_spawn_rate)

            for event in pygame.event.get():
                # Quit Game
                if event.type == pygame.QUIT:
                    run = False

                elif event.type == pygame.KEYDOWN:
                    # Quit Game            
                    if event.key == pygame.K_ESCAPE:
                        run = False

                    # Reset Environment
                    if event.key == pygame.K_BACKSPACE:
                        env.reset()

                    # Spawn Players
                    sp = spawnPlayers(event, knight_player_num, archer_player_num, knight_list, archer_list, all_sprites, knight_dict, archer_dict)
                    # Knight
                    knight_player_num, knight_list, all_sprites, knight_dict = sp.spawnKnight()
                    # Archer
                    archer_player_num, archer_list, all_sprites, archer_dict = sp.spawnArcher()

                    # Spawn Weapons
                    sw = spawnWeapons(event, sword_spawn_rate, arrow_spawn_rate, knight_killed, archer_killed, knight_dict, archer_dict, knight_list, archer_list, knight_player_num, archer_player_num, all_sprites, sword_dict, arrow_dict, sword_list, arrow_list)
                    # Sword
                    sword_spawn_rate, knight_killed, knight_dict, knight_list, knight_player_num, all_sprites, sword_dict, sword_list = sw.spawnSword()
                    # Arrow
                    arrow_spawn_rate, archer_killed, archer_dict, archer_list, archer_player_num, all_sprites, arrow_dict, arrow_list = sw.spawnArrow()

            # Spawning Zombies at Random Location at every 100 iterations
            zombie_spawn_rate, zombie_list, all_sprites = spawn_zombie(zombie_spawn_rate, zombie_list, all_sprites)

            # Stab the Sword
            sword_list, all_sprites = sword_stab(sword_list, all_sprites)

            # Zombie Kills the Arrow
            zombie_list, arrow_list, all_sprites, score = zombie_arrow(zombie_list, arrow_list, all_sprites, score)

            # Zombie Kills the Sword
            zombie_list, sword_list, all_sprites, score = zombie_sword(zombie_list, sword_list, all_sprites, score)

            # Zombie Kills the Archer
            zombie_archer(zombie_list, archer_list, all_sprites, archer_killed)

            # Zombie Kills the Knight
            zombie_list, knight_list, all_sprites, knight_killed, sword_list, sword_killed = zombie_knight(zombie_list, knight_list, all_sprites, knight_killed, sword_list, sword_killed)

            # Kill the Sword when Knight dies
            sword_killed, sword_list, all_sprites = kill_sword(sword_killed, sword_list, all_sprites)

            # Call the update() method on all the sprites
            all_sprites.update()

            WINDOW.fill(WHITE)
            all_sprites.draw(WINDOW)       # Draw all the sprites
            pygame.display.update()
            pygame.display.flip()               # update screen
            clock.tick(FPS)                      # FPS

            # Zombie reaches the End of the Screen
            run = zombie_endscreen(run, zombie_list)

            # Zombie Kills all Players
            run = zombie_all_players(knight_list, archer_list, run)

            # Condition to Check 900 Frames
            count += 1
            if count > 900:
                print('*** GAME OVER - 900 Frames Completed ***')
                run = False

    def reset(self):
        pass