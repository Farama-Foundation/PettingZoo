import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import sys
sys.dont_write_bytecode = True
import pygame
import pygame.gfxdraw
from .src.players import Knight, Archer
from .src.zombie import Zombie
from .src.weapons import Arrow, Sword
from .manual_control import manual_control
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import EnvLogger
from gym.spaces import Box, Discrete
from gym.utils import seeding


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, seed=0, spawn_rate=20, num_archers=2, num_knights=2, killable_knights=True, killable_archers=True, pad_observation=True, max_frames=900):
        # Game Constants
        self.ZOMBIE_SPAWN = spawn_rate
        self.FPS = 90
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.max_frames = 500
        self.frames = 0
        self.pad_observation = pad_observation
        self.killable_knights = killable_knights
        self.killable_archers = killable_archers
        self.has_reset = False
        self.np_random, seed = seeding.np_random(seed)

        # Dictionaries for holding new players and their weapons
        self.archer_dict = {}
        self.knight_dict = {}
        self.arrow_dict = {}
        self.sword_dict = {}

        # Game Variables
        self.frame_count = 0
        self.score = 0
        self.run = True
        self.arrow_spawn_rate = self.sword_spawn_rate = self.zombie_spawn_rate = 0
        self.knight_player_num = self.archer_player_num = 0
        self.archer_killed = False
        self.knight_killed = False
        self.sword_killed = False

        # Creating Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.zombie_list = pygame.sprite.Group()
        self.arrow_list = pygame.sprite.Group()
        self.sword_list = pygame.sprite.Group()
        self.archer_list = pygame.sprite.Group()
        self.knight_list = pygame.sprite.Group()

        self.num_archers = num_archers
        self.num_knights = num_knights

        # Initializing Pygame
        self.render_on = False
        pygame.init()
        # self.WINDOW = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.WINDOW = pygame.Surface((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Knights, Archers, Zombies")
        self.clock = pygame.time.Clock()
        self.left_wall = get_image(os.path.join('img', 'left_wall.png'))
        self.right_wall = get_image(os.path.join('img', 'right_wall.png'))
        self.right_wall_rect = self.right_wall.get_rect()
        self.right_wall_rect.left = self.WIDTH - self.right_wall_rect.width
        self.floor_patch1 = get_image(os.path.join('img', 'patch1.png'))
        self.floor_patch2 = get_image(os.path.join('img', 'patch2.png'))
        self.floor_patch3 = get_image(os.path.join('img', 'patch3.png'))
        self.floor_patch4 = get_image(os.path.join('img', 'patch4.png'))

        self.agent_list = []
        self.agents = []

        for i in range(num_archers):
            self.archer_dict["archer{0}".format(self.archer_player_num)] = Archer()
            self.archer_dict["archer{0}".format(self.archer_player_num)].offset(i * 50, 0)
            self.archer_list.add(self.archer_dict["archer{0}".format(self.archer_player_num)])
            self.all_sprites.add(self.archer_dict["archer{0}".format(self.archer_player_num)])
            self.agent_list.append(self.archer_dict["archer{0}".format(self.archer_player_num)])
            if i != num_archers - 1:
                self.archer_player_num += 1

        for i in range(num_knights):
            self.knight_dict["knight{0}".format(self.knight_player_num)] = Knight()
            self.knight_dict["knight{0}".format(self.knight_player_num)].offset(i * 50, 0)
            self.knight_list.add(self.knight_dict["knight{0}".format(self.knight_player_num)])
            self.all_sprites.add(self.knight_dict["knight{0}".format(self.knight_player_num)])
            self.agent_list.append(self.knight_dict["knight{0}".format(self.knight_player_num)])
            if i != num_knights - 1:
                self.knight_player_num += 1

        self.agent_name_mapping = {}
        a_count = 0
        for i in range(num_archers):
            a_name = "archer_" + str(i)
            self.agents.append(a_name)
            self.agent_name_mapping[a_name] = a_count
            a_count += 1
        for i in range(num_knights):
            k_name = "knight_" + str(i)
            self.agents.append(k_name)
            self.agent_name_mapping[k_name] = a_count
            a_count += 1

        self.observation_spaces = dict(zip(self.agents, [Box(low=0, high=255, shape=(512, 512, 3), dtype=np.uint8) for _ in enumerate(self.agents)]))
        self.action_spaces = dict(zip(self.agents, [Discrete(6) for _ in enumerate(self.agents)]))
        self.display_wait = 0.0

        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = 0
        self.num_agents = len(self.agents)
        self.reinit()

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
            # if self.event.key == pygame.K_m:
            #     self.knight_player_num += 1
            #     self.knight_dict['knight{0}'.format(self.knight_player_num)] = Knight()
            #     self.knight_list.add(self.knight_dict['knight{0}'.format(self.knight_player_num)])
            #     self.all_sprites.add(self.knight_dict['knight{0}'.format(self.knight_player_num)])
            return self.knight_player_num, self.knight_list, self.all_sprites, self.knight_dict

        # Spawn New Archer
        def spawnArcher(self):
            # if self.event.key == pygame.K_x:
            #     self.archer_player_num += 1
            #     self.archer_dict['archer{0}'.format(self.archer_player_num)] = Archer()
            #     self.archer_list.add(self.archer_dict['archer{0}'.format(self.archer_player_num)])
            #     self.all_sprites.add(self.archer_dict['archer{0}'.format(self.archer_player_num)])
            return self.archer_player_num, self.archer_list, self.all_sprites, self.archer_dict

    # Spawn New Weapons
    class spawnWeapons(pygame.sprite.Sprite):
        def __init__(self, action, agent_index, agent_list, sword_spawn_rate, arrow_spawn_rate, knight_killed, archer_killed,
                     knight_dict, archer_dict, knight_list, archer_list, knight_player_num, archer_player_num,
                     all_sprites, sword_dict, arrow_dict, sword_list, arrow_list):
            super().__init__()
            self.action = action
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

            self.agent_index = agent_index
            self.agent_list = agent_list

        # Spawning Swords for Players
        def spawnSword(self):
            if (self.action == 5 and self.sword_spawn_rate == 0 and self.agent_list[self.agent_index].is_knight):
                if not self.sword_list:      # Sword List is Empty
                    if not self.knight_killed:
                        for i in range(0, self.knight_player_num + 1):
                            self.sword_dict['sword{0}'.format(i)] = Sword((self.knight_dict['knight{0}'.format(i)]))
                            self.sword_list.add(self.sword_dict[('sword{0}'.format(i))])
                            self.all_sprites.add(self.sword_dict[('sword{0}'.format(i))])
                        self.sword_spawn_rate = 1
                        self.knight_killed = False
                    else:
                        for knight in self.knight_list:
                            temp = Sword(knight)
                            self.sword_list.add(temp)
                            self.all_sprites.add(temp)
                        self.sword_spawn_rate = 1
            return self.sword_spawn_rate, self.knight_killed, self.knight_dict, self.knight_list, self.knight_player_num, self.all_sprites, self.sword_dict, self.sword_list

        # Spawning Arrows for Players
        def spawnArrow(self):
            if (self.action == 5 and self.arrow_spawn_rate == 0 and self.agent_list[self.agent_index].is_archer):
                if not self.archer_killed:
                    for i in range(0, self.archer_player_num + 1):
                        if i == self.agent_index:
                            self.arrow_dict[('arrow{0}'.format(i))] = Arrow(self.archer_dict[('archer{0}'.format(i))])
                            self.arrow_list.add(self.arrow_dict[('arrow{0}'.format(i))])
                            self.all_sprites.add(self.arrow_dict[('arrow{0}'.format(i))])
                    self.arrow_spawn_rate = 1
                    self.archer_killed = False
                else:
                    for archer in self.archer_list:
                        temp = Arrow(archer)
                        self.arrow_list.add(temp)
                        self.all_sprites.add(temp)
                    self.arrow_spawn_rate = 1
            return self.arrow_spawn_rate, self.archer_killed, self.archer_dict, self.archer_list, self.archer_player_num, self.all_sprites, self.arrow_dict, self.arrow_list

    # Stab the Sword
    def sword_stab(self, sword_list, all_sprites):
        for sword in sword_list:
            sword_active = sword.update()
            if not sword_active:  # remove the sprite
                sword_list.remove(sword)
                all_sprites.remove(sword)

        return sword_list, all_sprites

    # Spawning Zombies at Random Location at every 100 iterations
    def spawn_zombie(self, zombie_spawn_rate, zombie_list, all_sprites):
        zombie_spawn_rate += 1
        zombie = Zombie()

        if zombie_spawn_rate >= self.ZOMBIE_SPAWN:
            zombie.rect.x = self.np_random.randint(0, self.WIDTH)
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
            if sword_killed:
                sword_list.remove(sword)
                all_sprites.remove(sword)
                sword_killed = False
        return sword_killed, sword_list, all_sprites

    # Zombie Kills the Archer
    def zombie_archer(self, zombie_list, archer_list, all_sprites, archer_killed):
        for zombie in zombie_list:
            zombie_archer_list = pygame.sprite.spritecollide(zombie, archer_list, True)

            for archer in zombie_archer_list:
                archer.alive = False
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
                # score += 1
                sword.knight.score += 1
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
                # score += 1
                arrow.archer.score += 1

            # Remove the arrow if it flies up off the screen
            if arrow.rect.y < 0:
                arrow_list.remove(arrow)
                all_sprites.remove(arrow)
        return zombie_list, arrow_list, all_sprites, score

    # Zombie reaches the End of the Screen
    def zombie_endscreen(self, run, zombie_list):
        for zombie in zombie_list:
            if zombie.rect.y > 690:
                run = False
        return run

    # Zombie Kills all Players
    def zombie_all_players(self, knight_list, archer_list, run):
        if not knight_list and not archer_list:
            run = False
        return run

    def observe(self, agent):
        if not self.has_reset:
            EnvLogger.error_observe_before_reset()
        screen = pygame.surfarray.pixels3d(self.WINDOW)

        i = self.agent_name_mapping[agent]
        agent_obj = self.agent_list[i]
        agent_position = (agent_obj.rect.x, agent_obj.rect.y)

        if not agent_obj.alive:
            cropped = np.zeros((512, 512, 3))
        else:
            min_x = agent_position[0] - 256
            max_x = agent_position[0] + 256
            min_y = agent_position[1] - 256
            max_y = agent_position[1] + 256
            lower_y_bound = max(min_y, 0)
            upper_y_bound = min(max_y, self.HEIGHT)
            lower_x_bound = max(min_x, 0)
            upper_x_bound = min(max_x, self.WIDTH)
            cropped = np.array(screen)
            cropped = cropped[lower_x_bound:upper_x_bound, :, :]
            cropped = cropped[:, lower_y_bound:upper_y_bound, :]
            if self.pad_observation:
                # Add blackness to the left side of the window
                if min_x < 0:
                    pad = np.zeros((abs(min_x), cropped.shape[1], 3))
                    cropped = np.vstack((pad, cropped))
                # Add blackness to the right side of the window
                if max_x > self.WIDTH:
                    pad = np.zeros(((max_x - self.WIDTH), cropped.shape[1], 3))
                    cropped = np.vstack((cropped, pad))
                # Add blackness to the top side of the window
                if min_y < 0:
                    pad = np.zeros((cropped.shape[0], abs(min_y), 3))
                    cropped = np.hstack((pad, cropped))
                # Add blackness to the bottom side of the window
                if max_y > self.HEIGHT:
                    pad = np.zeros((cropped.shape[0], (max_y - self.HEIGHT), 3))
                    cropped = np.hstack((cropped, pad))
            cropped = np.rot90(cropped, k=3)
            cropped = np.fliplr(cropped).astype(np.uint8)
        return cropped

    def step(self, action, observe=True):
        if not self.has_reset:
            EnvLogger.error_step_before_reset()
        agent = self.agent_selection
        if action is None or np.isnan(action):
            EnvLogger.warn_action_is_NaN(backup_policy="setting action to 1")
            action = 1
        elif not self.action_spaces[agent].contains(action):
            EnvLogger.warn_action_out_of_bound(action=action, action_space=self.action_spaces[agent], backup_policy="setting action to 1")
            action = 1
        if self.render_on:
            self.clock.tick(self.FPS)                # FPS
        else:
            self.clock.tick()
        if self._agent_selector.is_last():
            # Controls the Spawn Rate of Weapons
            self.sword_spawn_rate, self.arrow_spawn_rate = self.check_weapon_spawn(self.sword_spawn_rate, self.arrow_spawn_rate)

            # Keyboard input check
            for event in pygame.event.get():
                # Quit Game
                if event.type == pygame.QUIT:
                    self.run = False

                elif event.type == pygame.KEYDOWN:
                    # Quit Game
                    if event.key == pygame.K_ESCAPE:
                        self.run = False

                    # Reset Environment
                    if event.key == pygame.K_BACKSPACE:
                        self.reset(observe=False)
        agent_name = self.agent_list[self.agent_name_mapping[agent]]
        agent_name.update(action)

        sp = self.spawnPlayers(action, self.knight_player_num, self.archer_player_num, self.knight_list, self.archer_list, self.all_sprites, self.knight_dict, self.archer_dict)
        # Knight
        self.knight_player_num, self.knight_list, self.all_sprites, self.knight_dict = sp.spawnKnight()
        # Archer
        self.archer_player_num, self.archer_list, self.all_sprites, self.archer_dict = sp.spawnArcher()
        # Spawn Weapons
        sw = self.spawnWeapons(action, self.agent_name_mapping[agent], self.agent_list, self.sword_spawn_rate, self.arrow_spawn_rate, self.knight_killed, self.archer_killed, self.knight_dict, self.archer_dict, self.knight_list, self.archer_list, self.knight_player_num, self.archer_player_num, self.all_sprites, self.sword_dict, self.arrow_dict, self.sword_list, self.arrow_list)
        # Sword
        self.sword_spawn_rate, self.knight_killed, self.knight_dict, self.knight_list, self.knight_player_num, self.all_sprites, self.sword_dict, self.sword_list = sw.spawnSword()
        # Arrow
        self.arrow_spawn_rate, self.archer_killed, self.archer_dict, self.archer_list, self.archer_player_num, self.all_sprites, self.arrow_dict, self.arrow_list = sw.spawnArrow()
        if self._agent_selector.is_last():
            # Spawning Zombies at Random Location at every 100 iterations
            self.zombie_spawn_rate, self.zombie_list, self.all_sprites = self.spawn_zombie(self.zombie_spawn_rate, self.zombie_list, self.all_sprites)

            # Stab the Sword
            self.sword_list, self.all_sprites = self.sword_stab(self.sword_list, self.all_sprites)

            # Zombie Kills the Arrow
            self.zombie_list, self.arrow_list, self.all_sprites, self.score = self.zombie_arrow(self.zombie_list, self.arrow_list, self.all_sprites, self.score)

            # Zombie Kills the Sword
            self.zombie_list, self.sword_list, self.all_sprites, self.score = self.zombie_sword(self.zombie_list, self.sword_list, self.all_sprites, self.score)

            # Zombie Kills the Archer
            if self.killable_archers:
                self.zombie_archer(self.zombie_list, self.archer_list, self.all_sprites, self.archer_killed)

            # Zombie Kills the Knight
            if self.killable_knights:
                self.zombie_list, self.knight_list, self.all_sprites, self.knight_killed, self.sword_list, self.sword_killed = self.zombie_knight(self.zombie_list, self.knight_list, self.all_sprites, self.knight_killed, self.sword_list, self.sword_killed)

            # Kill the Sword when Knight dies
            self.sword_killed, self.sword_list, self.all_sprites = self.kill_sword(self.sword_killed, self.sword_list, self.all_sprites)

            for zombie in self.zombie_list:
                zombie.update()
            arrows_to_delete = []

            for arrow in self.arrow_list:
                arrow.update()
                if not arrow.is_active():
                    arrows_to_delete.append(arrow)
            for arrow in arrows_to_delete:
                self.arrow_list.remove(arrow)
                self.all_sprites.remove(arrow)

            self.WINDOW.fill((66, 40, 53))
            self.WINDOW.blit(self.left_wall, self.left_wall.get_rect())
            self.WINDOW.blit(self.right_wall, self.right_wall_rect)
            self.WINDOW.blit(self.floor_patch1, (500, 500))
            self.WINDOW.blit(self.floor_patch2, (900, 30))
            self.WINDOW.blit(self.floor_patch3, (150, 430))
            self.WINDOW.blit(self.floor_patch4, (300, 50))
            self.WINDOW.blit(self.floor_patch1, (1000, 250))
            self.all_sprites.draw(self.WINDOW)       # Draw all the sprites

            self.check_game_end()
            self.frames += 1
        self.agent_selection = self._agent_selector.next()
        self.rewards[agent] = agent_name.score
        self.dones[agent] = not self.run or self.frames >= self.max_frames
        if observe:
            return self.observe(self.agent_selection)

    def enable_render(self):
        self.WINDOW = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        # self.WINDOW = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.render_on = True
        self.reset()

    def render(self, mode="human"):
        if not self.render_on:
            # sets self.render_on to true and initializes display
            self.enable_render()
        pygame.display.flip()

    def close(self):
        if not self.render_on:
            EnvLogger.warn_close_unrendered_env()
        else:
            # self.WINDOW = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
            self.WINDOW = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.render_on = False
            pygame.event.pump()
            pygame.display.quit()

    def check_game_end(self):
        # Zombie reaches the End of the Screen
        self.run = self.zombie_endscreen(self.run, self.zombie_list)

        # Zombie Kills all Players
        self.run = self.zombie_all_players(self.knight_list, self.archer_list, self.run)

        # Condition to Check 900 Frames
        self.frame_count += 1
        if self.frame_count > 900:
            self.run = False

    def reinit(self):
        # Dictionaries for holding new players and their weapons
        self.archer_dict = {}
        self.knight_dict = {}
        self.arrow_dict = {}
        self.sword_dict = {}

        # Game Variables
        self.frame_count = 0
        self.score = 0
        self.run = True
        self.arrow_spawn_rate = self.sword_spawn_rate = self.zombie_spawn_rate = 0
        self.knight_player_num = self.archer_player_num = 0
        self.archer_killed = False
        self.knight_killed = False
        self.sword_killed = False

        # Creating Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.zombie_list = pygame.sprite.Group()
        self.arrow_list = pygame.sprite.Group()
        self.sword_list = pygame.sprite.Group()
        self.archer_list = pygame.sprite.Group()
        self.knight_list = pygame.sprite.Group()

        self.agent_list = []
        self.agents = []

        for i in range(self.num_archers):
            self.archer_dict["archer{0}".format(self.archer_player_num)] = Archer()
            self.archer_dict["archer{0}".format(self.archer_player_num)].offset(i * 50, 0)
            self.archer_list.add(self.archer_dict["archer{0}".format(self.archer_player_num)])
            self.all_sprites.add(self.archer_dict["archer{0}".format(self.archer_player_num)])
            self.agent_list.append(self.archer_dict["archer{0}".format(self.archer_player_num)])
            if i != self.num_archers - 1:
                self.archer_player_num += 1

        for i in range(self.num_knights):
            self.knight_dict["knight{0}".format(self.knight_player_num)] = Knight()
            self.knight_dict["knight{0}".format(self.knight_player_num)].offset(i * 50, 0)
            self.knight_list.add(self.knight_dict["knight{0}".format(self.knight_player_num)])
            self.all_sprites.add(self.knight_dict["knight{0}".format(self.knight_player_num)])
            self.agent_list.append(self.knight_dict["knight{0}".format(self.knight_player_num)])
            if i != self.num_knights - 1:
                self.knight_player_num += 1

        self.agent_name_mapping = {}
        a_count = 0
        for i in range(self.num_archers):
            a_name = "archer_" + str(i)
            self.agents.append(a_name)
            self.agent_name_mapping[a_name] = a_count
            a_count += 1
        for i in range(self.num_knights):
            k_name = "knight_" + str(i)
            self.agents.append(k_name)
            self.agent_name_mapping[k_name] = a_count
            a_count += 1

        self.agent_order = self.agents[:]
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()

        self.frames = 0

    def reset(self, observe=True):
        self.has_reset = True
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.reinit()
        if observe:
            return self.observe(self.agent_selection)

# The original code for this game, that was added by Justin Terry, was
# created by Dipam Patel in a different repository (hence the git history)

# Game art puchased from https://finalbossblues.itch.io/time-fantasy-monsters

# and https://finalbossblues.itch.io/icons
