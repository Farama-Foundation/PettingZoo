import copy
import math
import sys
import os
from lxml import etree
import lxml.builder    

import gym
import numpy as np
from gym import spaces
from gym import utils
from gym.utils import seeding
from gym.envs.mujoco import mujoco_env

from madrl_environments import AbstractMAEnv, Agent

from rltools.util import EzPickle


class AntLeg(Agent):

    def __init__(self, model, idx, n_legs,
                 pos_noise=1e-3,
                 vel_noise=1e-3,
                 force_noise=1e-3):
        self._idx = idx
        self.n_legs = n_legs
        self.model = model

        self.pos_noise = pos_noise
        self.vel_noise = vel_noise
        self.force_noise = force_noise


    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
 

    @property
    def action_space(self):
        return spaces.Box(low=-1, high=1, shape=(2,))

    @property
    def observation_space(self):
        # 18 force observations for each leg + 4 pos + vel per leg (2 neighboring legs) + 11 world coords
        return spaces.Box(low=-np.inf, high=np.inf, shape=(18 + 4 + 4 + 4 + 11,))

    
    def get_observation(self):
        idx = self._idx
        n1_idx = idx-1 if idx > 0 else self.n_legs-1
        n2_idx = idx+1 if idx < (self.n_legs - 1) else 0
        return np.concatenate([
            np.random.normal(self.model.data.qpos.flat[2:7], self.pos_noise), # body pos
            np.random.normal(self.model.data.qvel.flat[:6], self.vel_noise), # body vel
            np.random.normal(self.model.data.qpos.flat[7+2*idx:9+2*idx], self.pos_noise),
            np.random.normal(self.model.data.qvel.flat[6+2*idx:8+2*idx], self.vel_noise),
            np.random.normal(self.model.data.qpos.flat[7+2*n1_idx:9+2*n1_idx], self.pos_noise),
            np.random.normal(self.model.data.qvel.flat[6+2*n1_idx:8+2*n1_idx], self.vel_noise),
            np.random.normal(self.model.data.qpos.flat[7+2*n2_idx:9+2*n2_idx], self.pos_noise),
            np.random.normal(self.model.data.qvel.flat[6+2*n2_idx:8+2*n2_idx], self.vel_noise),
            np.random.normal(np.clip(self.model.data.cfrc_ext[3*idx+2:3*idx+5], -1, 1).flat, self.force_noise)
        ])


class MultiAnt(EzPickle, mujoco_env.MujocoEnv):

    def __init__(self, 
                 n_legs=4,
                 ts=0.02,
                 integrator='RK4',
                 leg_length=0.282,
                 out_file="multi_ant.xml",
                 base_file="ant_og.xml",
                 reward_mech='local',
                 pos_noise=1e-3,
                 vel_noise=1e-3,
                 force_noise=1e-3
                 ):
        EzPickle.__init__(self, n_legs, ts, integrator, leg_length,
                                out_file, base_file, reward_mech,
                                pos_noise, vel_noise, force_noise)
        self.n_legs = n_legs
        self.ts = ts
        self.integrator = integrator
        self.leg_length = leg_length
        self.out_file = out_file
        self.base_file = base_file
        self._reward_mech = reward_mech
        
        self.pos_noise = pos_noise
        self.vel_noise = vel_noise
        self.force_noise = force_noise

        self.legs = None
        self.out_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.out_file)
        self.base_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.base_file)

        self.gen_xml(out_file=self.out_file_path, og_file=self.base_file_path)

        mujoco_env.MujocoEnv.__init__(self, self.out_file_path, 5)
        self.legs = [AntLeg(self.model, i, n_legs, pos_noise=pos_noise, vel_noise=vel_noise, force_noise=force_noise) for i in range(self.n_legs)]


    @property
    def agents(self):
        return self.legs


    @property
    def reward_mech(self):
        return self._reward_mech


    def seed(self, seed=None):
        self.np_random, seed_ = seeding.np_random(seed)
        return [seed_]


    def setup(self):
        self.seed()

        self.gen_xml(out_file=self.out_file_path, og_file=self.base_file_path)

        mujoco_env.MujocoEnv.__init__(self, self.out_file_path, 5)
        self.legs = [AntLeg(self.model, i, self.n_legs, pos_noise=self.pos_noise, vel_noise=self.vel_noise,
            force_noise=self.force_noise) for i in range(self.n_legs)]


    def _step(self, a):
        xposbefore = self.get_body_com("torso")[0]
        self.do_simulation(a, self.frame_skip)
        xposafter = self.get_body_com("torso")[0]
        forward_reward = (xposafter - xposbefore)/self.dt
        ctrl_cost = .5 * np.square(a).sum()
        contact_cost = 0.5 * 1e-3 * np.sum(
            np.square(np.clip(self.model.data.cfrc_ext, -1, 1)))
        survive_reward = 1.0
        reward = forward_reward - ctrl_cost - contact_cost + survive_reward
        state = self.state_vector()
        notdone = np.isfinite(state).all() \
            and state[2] >= 0.26 and state[2] <= 1.0
        done = not notdone
        ob = self._get_obs()
        return ob, [reward]*self.n_legs, done, dict(
            reward_forward=forward_reward,
            reward_ctrl=-ctrl_cost,
            reward_contact=-contact_cost,
            reward_survive=survive_reward)

    def _get_obs(self):
        obs = [l.get_observation() for l in self.legs] if self.legs else np.random.rand(self.n_legs, 32)
        return np.array(obs)

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(size=self.model.nq,low=-.1,high=.1)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.set_state(qpos, qvel)
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = self.model.stat.extent * 0.5



    def gen_xml(self, out_file="ant.xml",
                      og_file="ant_og.xml"):
        """Write .xml file for the ant problem.
        Modify original 4 leg ant defintion.
        """

        self.init_geometry()

        parser = etree.XMLParser(remove_blank_text=True)
        og = etree.parse(og_file, parser)


        # add legs
        torso = og.find('.//body')
        # first remove original legs
        for c in torso.getchildren():
            if c.tag == 'body':
                torso.remove(c)
        for i in range(self.n_legs):
            # 1st half leg
            leg = etree.SubElement(torso, "body",
                                   name="leg_"+str(i),
                                   pos="0 0 0")
            etree.SubElement(leg, "geom",
                             name="aux_"+str(i)+"_geom",
                             type="capsule",
                             size="0.08",
                             fromto="0.0 0.0 0.0 "+self.leg_geom_string[i])
            # Hip joint
            aux = etree.SubElement(leg, "body",
                                   name="aux_"+str(i),
                                   pos=self.leg_geom_string[i])
            etree.SubElement(aux, "joint",
                             name="hip_"+str(i),
                             type="hinge",
                             pos="0.0 0.0 0.0",
                             axis="0 0 1",
                             range="-30 30")
            etree.SubElement(aux, "geom",
                             name="leg_geom_"+str(i),
                             type="capsule",
                             size="0.08",
                             fromto="0.0 0.0 0.0 "+self.leg_geom_string[i])
            # ankle joint
            ankle = etree.SubElement(aux, "body",
                                     pos=self.leg_geom_string[i])
            etree.SubElement(ankle, "joint",
                             name="ankle_"+str(i),
                             type="hinge",
                             pos="0.0 0.0 0.0",
                             axis=self.leg_axis[i],
                             range=self.angle_range[i])
            etree.SubElement(ankle, "geom",
                             name="ankle_geom_"+str(i),
                             type="capsule",
                             size="0.08",
                             fromto="0.0 0.0 0.0 "+self.leg_geom_string_2x[i])
                            

        # add new motors
        actuators = og.find('actuator')
        actuators.clear()
        for i in range(self.n_legs):
            etree.SubElement(actuators, "motor",
                                        joint="hip_"+str(i),
                                        ctrlrange="-150.0 150.0",
                                        ctrllimited="true")
            etree.SubElement(actuators, "motor",
                                        joint="ankle_"+str(i),
                                        ctrlrange="-150.0 150.0",
                                        ctrllimited="true")

        og.write(out_file, pretty_print=True)


    def init_geometry(self):
        self.gen_leg_geometry()


    def gen_leg_geometry(self):
        self.leg_geom = np.zeros((self.n_legs, 3))
        self.leg_geom_string = []
        self.leg_geom_string_2x = []
        self.leg_axis = []
        self.angle_range = []
        for i in range(self.n_legs):
            x, y = np.round(self.get_point_on_circle(self.leg_length, i, self.n_legs), decimals=5)
            self.leg_geom[i,:] = np.array([x,y,0.0])
            self.leg_geom_string.append(str(x) + " " + str(y) + " " + "0.0")
            self.leg_geom_string_2x.append(str(2*x) + " " + str(2*y) + " " + "0.0")
            # TODO (max): y no switch?
            if (x >= 0.0 and y >= 0.0):
                self.angle_range.append("30 70")
                self.leg_axis.append("-1 1 0")
            elif (x > 0.0 and y < 0.0):
                self.angle_range.append("30 70")
                self.leg_axis.append("1 1 0")
            elif (x <= 0.0 and y <= 0.0):
                self.angle_range.append("-70 -30")
                self.leg_axis.append("-1 1 0")
            else:
                self.angle_range.append("-70 -30")
                self.leg_axis.append("1 1 0")


    def get_point_on_circle(self, r, current_point, total_points):
        theta = 2*np.pi / total_points 
        angle = theta * current_point + np.pi/self.n_legs
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        return x, y


    def set_param_values(self, lut):
        for k, v in lut.items():
            setattr(self, k, v)
        self.setup()

    def get_param_values(self):
        return self.__dict__


if __name__ == '__main__':
    env = MultiAnt(4)
    env.reset()
    for i in range(250):
        env.render()
        a = np.array([l.action_space.sample() for l in env.agents])
        o, r, done, _ = env.step(a)
        print("\nStep:", i)
        print("Rewards:", r)
        if done:
            break
