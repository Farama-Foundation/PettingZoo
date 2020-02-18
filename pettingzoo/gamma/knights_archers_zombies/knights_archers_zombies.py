import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import sys
sys.dont_write_bytecode = True
import pygame
import random
import pygame.gfxdraw
from .src.players import Knight, Archer
from .src.zombie import Zombie
from .src.weapons import Arrow, Sword
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt
from ray.rllib.env.multi_agent_env import MultiAgentEnv


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image

class env(MultiAgentEnv):
    def __init__(self, num_archers=2, num_knights=2):
        # Game Constants
        self.ZOMBIE_SPAWN = 20
        self.SPAWN_STAB_RATE = 20
        self.FPS = 15
        self.WIDTH = 1280
        self.HEIGHT = 720

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
        self.agent_ids = []
        self.num_agents = num_archers + num_knights

        # TODO: add zombie spawn rate parameter? and add max # of timesteps parameter?
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

        for i in range(num_archers + num_knights):
            self.agent_ids.append(i)

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
        try:
            for sword in sword_list:
                sword_active = sword.update()
                if not sword_active:  # remove the sprite
                    sword_list.remove(sword)
                    all_sprites.remove(sword)
        except:
            pass
        return sword_list, all_sprites

    # Spawning Zombies at Random Location at every 100 iterations
    def spawn_zombie(self, zombie_spawn_rate, zombie_list, all_sprites):
        zombie_spawn_rate += 1
        zombie = Zombie()

        if zombie_spawn_rate >= self.ZOMBIE_SPAWN:
            zombie.rect.x = random.randrange(self.WIDTH)
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

    def observe(self):
        observation = pygame.surfarray.array3d(self.WINDOW)
        observation = np.rot90(observation, k=3)
        observation = np.fliplr(observation)
        observation = observation[:, :, 0]  # take red channel only instead of doing full greyscale

        agent_positions = []
        for agent in self.agent_list:
            agent_positions.append([agent.rect.y, agent.rect.x])  # y first because the 2d array is row-major

        observations = {}
        for i in range(len(self.agent_list)):
            min_x = agent_positions[i][1] - (32 * 8)
            max_x = agent_positions[i][1] + (32 * 8)
            min_y = agent_positions[i][0] - (32 * 8)
            max_y = agent_positions[i][0] + (32 * 8)
            cropped = observation[max(min_y, 0):min(max_y, self.HEIGHT), max(min_x, 0):min(max_x, self.WIDTH)]

            # Add blackness to the left side of the window
            if min_x < 0:
                pad = np.zeros((abs(min_x)) * cropped.shape[0]).reshape(cropped.shape[0], abs(min_x))
                cropped = np.hstack((pad, cropped))
            # Add blackness to the right side of the window
            if max_x > self.WIDTH:
                pad = np.zeros((max_x - self.WIDTH) * cropped.shape[0]).reshape(cropped.shape[0], max_x - self.WIDTH)
                cropped = np.hstack((cropped, pad))
            # Add blackness to the top side of the window
            if min_y < 0:
                pad = np.zeros(abs(min_y) * cropped.shape[1]).reshape(abs(min_y), cropped.shape[1])
                cropped = np.vstack((pad, cropped))
            # Add blackness to the bottom side of the window
            if max_y > self.HEIGHT:
                pad = np.zeros((max_y - self.HEIGHT) * cropped.shape[1]).reshape(max_y - self.HEIGHT, cropped.shape[1])
                cropped = np.vstack((cropped, pad))

            mean = lambda x, axis: np.mean(x, axis=axis, dtype=np.uint8)
            cropped = measure.block_reduce(cropped, block_size=(10, 10), func=mean)  # scale to 40x40

            unscaled_obs = np.expand_dims(cropped, axis=2).flatten()
            observations[self.agent_ids[i]] = np.divide(unscaled_obs, 255, dtype=np.float32)

        return observations

    # Advance game state by 1 timestep
    def step(self, actions):
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
                    self.reset()

        # Handle agent control
        for i, agent in enumerate(self.agent_list):
            # Spawn Players
            sp = self.spawnPlayers(actions[i], self.knight_player_num, self.archer_player_num, self.knight_list, self.archer_list, self.all_sprites, self.knight_dict, self.archer_dict)
            # Knight
            self.knight_player_num, self.knight_list, self.all_sprites, self.knight_dict = sp.spawnKnight()
            # Archer
            self.archer_player_num, self.archer_list, self.all_sprites, self.archer_dict = sp.spawnArcher()

            # Spawn Weapons
            sw = self.spawnWeapons(actions[i], i, self.agent_list, self.sword_spawn_rate, self.arrow_spawn_rate, self.knight_killed, self.archer_killed, self.knight_dict, self.archer_dict, self.knight_list, self.archer_list, self.knight_player_num, self.archer_player_num, self.all_sprites, self.sword_dict, self.arrow_dict, self.sword_list, self.arrow_list)
            # Sword
            self.sword_spawn_rate, self.knight_killed, self.knight_dict, self.knight_list, self.knight_player_num, self.all_sprites, self.sword_dict, self.sword_list = sw.spawnSword()
            # Arrow
            self.arrow_spawn_rate, self.archer_killed, self.archer_dict, self.archer_list, self.archer_player_num, self.all_sprites, self.arrow_dict, self.arrow_list = sw.spawnArrow()

            agent.update(actions[i])

        # Spawning Zombies at Random Location at every 100 iterations
        self.zombie_spawn_rate, self.zombie_list, self.all_sprites = self.spawn_zombie(self.zombie_spawn_rate, self.zombie_list, self.all_sprites)

        # Stab the Sword
        self.sword_list, self.all_sprites = self.sword_stab(self.sword_list, self.all_sprites)

        # Zombie Kills the Arrow
        self.zombie_list, self.arrow_list, self.all_sprites, self.score = self.zombie_arrow(self.zombie_list, self.arrow_list, self.all_sprites, self.score)

        # Zombie Kills the Sword
        self.zombie_list, self.sword_list, self.all_sprites, self.score = self.zombie_sword(self.zombie_list, self.sword_list, self.all_sprites, self.score)

        # Zombie Kills the Archer
        self.zombie_archer(self.zombie_list, self.archer_list, self.all_sprites, self.archer_killed)

        # Zombie Kills the Knight
        self.zombie_list, self.knight_list, self.all_sprites, self.knight_killed, self.sword_list, self.sword_killed = self.zombie_knight(self.zombie_list, self.knight_list, self.all_sprites, self.knight_killed, self.sword_list, self.sword_killed)

        # Kill the Sword when Knight dies
        self.sword_killed, self.sword_list, self.all_sprites = self.kill_sword(self.sword_killed, self.sword_list, self.all_sprites)

        # Call the update() method on sprites
        for zombie in self.zombie_list:
            zombie.update()
        arrows_to_delete = []

        for arrow in self.arrow_list:
            arrow.update()
            if not arrow.is_active():
                arrows_to_delete.append(arrow)
        # delete arrows so they don't get rendered
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
        # pygame.display.update()
        # pygame.display.flip()                    # update screen
        if self.render_on:
            self.clock.tick(self.FPS)                # FPS
        else:
            self.clock.tick()

        self.check_game_end()

        reward_dict = dict(zip(self.agent_ids, [agent.score for agent in self.agent_list]))

        agent_done = [agent.is_done() for agent in self.agent_list]
        done_dict = dict(zip(self.agent_ids, agent_done))
        done_dict['__all__'] = not self.run

        observation = self.observe()

        return observation, reward_dict, done_dict, {}

    def enable_render(self):
        self.WINDOW = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        # self.WINDOW = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.render_on = True
        self.reset()

    def render(self):
        if not self.render_on:
            # sets self.render_on to true and initializes display
            self.enable_render()
        pygame.display.flip()

    def close(self):
        # self.WINDOW = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.WINDOW = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.render_on = False
        pygame.display.quit()

    def plot_obs(self, observation, fname):
        # shrink observation dims
        # shape = original_obs_shape(self.s_width, self.s_height)
        shape = (40, 40)
        for i in range(len(observation)):
            observation[i] = np.squeeze(observation[i])
            observation[i] = observation[i].reshape(shape)

        fig = plt.figure()
        # plt.imsave('test.png', observation[0], cmap = plt.cm.gray)
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)
        ax1.imshow(observation[0], cmap=plt.cm.gray)
        ax2.imshow(observation[1], cmap=plt.cm.gray)
        ax3.imshow(observation[2], cmap=plt.cm.gray)
        ax4.imshow(observation[3], cmap=plt.cm.gray)
        ax1.set_title("Observation[0]")
        ax2.set_title("Observation[1]")
        ax3.set_title("Observation[2]")
        ax4.set_title("Observation[3]")
        plt.savefig(fname)
        quit()

    def check_game_end(self):
        # Zombie reaches the End of the Screen
        self.run = self.zombie_endscreen(self.run, self.zombie_list)

        # Zombie Kills all Players
        self.run = self.zombie_all_players(self.knight_list, self.archer_list, self.run)

        # Condition to Check 900 Frames
        self.frame_count += 1
        if self.frame_count > 900:
            self.run = False

    def reset(self):
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
        self.agent_ids = []

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

        for i in range(self.num_archers + self.num_knights):
            self.agent_ids.append(i)

from .manual_test import manual_control
