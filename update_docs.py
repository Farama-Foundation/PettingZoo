from pettingzoo import butterfly
from pettingzoo.butterfly import prospector_v4, cooperative_pong_v3, knights_archers_zombies_v7, pistonball_v4, prison_v3
from pettingzoo.classic import backgammon_v3, checkers_v3, chess_v5, connect_four_v3, dou_dizhu_v4, gin_rummy_v4, go_v5, hanabi_v4, leduc_holdem_v4, mahjong_v4, rps_v2, texas_holdem_v4, texas_holdem_no_limit_v6, tictactoe_v3, uno_v4
from pettingzoo.magent import adversarial_pursuit_v3, battle_v3, battlefield_v3, combined_arms_v5, gather_v3, tiger_deer_v3
from pettingzoo.mpe import simple_adversary_v2, simple_crypto_v2, simple_push_v2, simple_reference_v2, simple_speaker_listener_v3, simple_spread_v2, simple_tag_v2, simple_v2, simple_world_comm_v2
from pettingzoo.sisl import multiwalker_v7, pursuit_v4, waterworld_v3
from pettingzoo.atari import basketball_pong_v2, boxing_v1, combat_plane_v1, combat_tank_v1, double_dunk_v2, entombed_competitive_v2, entombed_cooperative_v2, flag_capture_v1, foozpong_v2, ice_hockey_v1, joust_v2, mario_bros_v2, maze_craze_v2, othello_v2, pong_v2, quadrapong_v3, space_invaders_v1, space_war_v1, surround_v1, tennis_v2, video_checkers_v3, volleyball_pong_v2, warlords_v2, wizard_of_wor_v2
import numpy as np
import re
import gym

def create_string (values):
    string = ""
    for value in values:
        if string == "":
            string = str(value)
        else:
            string = string + ", " + str(value)
    return string

def determine_obs_shape (file):
    agents = file.agents
    values = []
    for agent in agents:
        if ((file.observation_space(agent)).shape) == None:
            if ((file.observation_space(agent))['observation'].shape) not in values:
                values.append((file.observation_space(agent))['observation'].shape)
        elif ((file.observation_space(agent)).shape) == ():
            if (file.observation_space(agent)) not in values:
                values.append(file.observation_space(agent))
        else:
            if ((file.observation_space(agent)).shape) not in values:
                values.append((file.observation_space(agent)).shape)
    return create_string(values)

def determine_obs_values (file):
    agents = file.agents
    values = []
    for agent in agents:
        if ((file.observation_space(agent)).shape) == None:
            if (np.amin((file.observation_space(agent))['observation'].low), np.amax((file.observation_space(agent))['observation'].high)) not in values:
                values.append((np.amin((file.observation_space(agent))['observation'].low), np.amax((file.observation_space(agent))['observation'].high)))
        elif ((file.observation_space(agent)).shape) == ():
            if (file.observation_space(agent)) not in values:
                values.append(file.observation_space(agent))
        else:
            if (np.amin((file.observation_space(agent)).low), np.amax((file.observation_space(agent)).high)) not in values:
                values.append((np.amin((file.observation_space(agent)).low), np.amax((file.observation_space(agent)).high)))
    return create_string(values)

def determine_act_shape (file):
    agents = file.agents
    values = []
    for agent in agents:
        if ((file.action_space(agent)).shape) == ():
            if (file.action_space(agent)) not in values:
                values.append(file.action_space(agent))
        else:
            if ((file.action_space(agent)).shape) not in values:
                values.append((file.action_space(agent)).shape)
    return create_string(values)

def determine_act_values (file):
    agents = file.agents
    values = []
    for agent in agents:
        if ((file.action_space(agent)).shape) == ():
            if (file.action_space(agent)) not in values:
                values.append(file.action_space(agent))
        else:
            if (np.amin((file.action_space(agent)).low), np.amax((file.action_space(agent)).high)) not in values:
                values.append((np.amin((file.action_space(agent)).low), np.amax((file.action_space(agent)).high)))
    return create_string(values)

def determine_state_shape (file):
    values = []
    if (file.state_space.shape) == ():
        if (file.state_space) not in values:
            values.append(file.state_space)
    else:
        if (file.state_space.shape) not in values:
            values.append(file.state_space.shape)
    return create_string(values)

def determine_state_values (file):
    values = []
    if (file.state_space.shape) == ():
        if (file.state_space) not in values:
            values.append(file.state_space)
    else:
        if (np.amin(file.state_space.low), np.amax(file.state_space.high)) not in values:
            values.append((np.amin(file.state_space.low), np.amax(file.state_space.high)))
    return create_string(values)

# Load the file into file_content
files = {
    'basketball_pong' : { 'markdown': 'basketball_pong.md', 'code' : 'pettingzoo/atari/basketball_pong_v2.py', 'environment' : (basketball_pong_v2.raw_env())},
    'boxing' : { 'markdown': 'boxing.md', 'code' : 'pettingzoo/atari/boxing_v1.py', 'environment' : (boxing_v1.raw_env())},
    'combat_plane' : { 'markdown': 'combat_plane.md', 'code' : 'pettingzoo/atari/combat_plane_v1.py', 'environment' : (combat_plane_v1.raw_env())},
    'combat_tank' : { 'markdown': 'combat_tank.md', 'code' : 'pettingzoo/atari/combat_tank_v1.py', 'environment' : (combat_tank_v1.raw_env())},
    'double_dunk' : { 'markdown': 'double_dunk.md', 'code' : 'pettingzoo/atari/double_dunk_v2.py', 'environment' : (double_dunk_v2.raw_env())},
    'entombed_competitive' : { 'markdown': 'entombed_competitive.md', 'code' : 'pettingzoo/atari/entombed_competitive_v2.py', 'environment' : (entombed_competitive_v2.raw_env())},
    'entombed_cooperative' : { 'markdown': 'entombed_cooperative.md', 'code' : 'pettingzoo/atari/entombed_cooperative_v2.py', 'environment' : (entombed_cooperative_v2.raw_env())},
    'flag_capture' : { 'markdown': 'flag_capture.md', 'code' : 'pettingzoo/atari/flag_capture_v1.py', 'environment' : (flag_capture_v1.raw_env())},
    'foozpong' : { 'markdown': 'foozpong.md', 'code' : 'pettingzoo/atari/foozpong_v2.py', 'environment' : (foozpong_v2.raw_env())},
    'ice_hockey' : { 'markdown': 'ice_hockey.md', 'code' : 'pettingzoo/atari/ice_hockey_v1.py', 'environment' : (ice_hockey_v1.raw_env())},
    'joust' : { 'markdown': 'joust.md', 'code' : 'pettingzoo/atari/joust_v2.py', 'environment' : (joust_v2.raw_env())},
    'mario_bros' : { 'markdown': 'mario_bros.md', 'code' : 'pettingzoo/atari/mario_bros_v2.py', 'environment' : (mario_bros_v2.raw_env())},
    'maze_craze' : { 'markdown': 'maze_craze.md', 'code' : 'pettingzoo/atari/maze_craze_v2.py', 'environment' : (maze_craze_v2.raw_env())},
    'othello' : { 'markdown': 'othello.md', 'code' : 'pettingzoo/atari/othello_v2.py', 'environment' : (othello_v2.raw_env())},
    'pong' : { 'markdown': 'pong.md', 'code' : 'pettingzoo/atari/pong_v2.py', 'environment' : (pong_v2.raw_env())},
    'quadrapong' : { 'markdown': 'quadrapong.md', 'code' : 'pettingzoo/atari/quadrapong_v3.py', 'environment' : (quadrapong_v3.raw_env())},
    'space_invaders' : { 'markdown': 'space_invaders.md', 'code' : 'pettingzoo/atari/space_invaders_v1.py', 'environment' : (space_invaders_v1.raw_env())},
    'space_war' : { 'markdown': 'space_war.md', 'code' : 'pettingzoo/atari/space_war_v1.py', 'environment' : (space_war_v1.raw_env())},
    'surround' : { 'markdown': 'surround.md', 'code' : 'pettingzoo/atari/surround_v1.py', 'environment' : (surround_v1.raw_env())},
    'tennis' : { 'markdown': 'tennis.md', 'code' : 'pettingzoo/atari/tennis_v2.py', 'environment' : (tennis_v2.raw_env())},
    'video_checkers' : { 'markdown': 'video_checkers.md', 'code' : 'pettingzoo/atari/video_checkers_v3.py', 'environment' : (video_checkers_v3.raw_env())},
    'volleyball_pong' : { 'markdown': 'volleyball_pong.md', 'code' : 'pettingzoo/atari/volleyball_pong_v2.py', 'environment' : (volleyball_pong_v2.raw_env())},
    'warlords' : { 'markdown': 'warlords.md', 'code' : 'pettingzoo/atari/warlords_v2.py', 'environment' : (warlords_v2.raw_env())},
    'wizards_of_wor' : { 'markdown': 'wizards_of_wor.md', 'code' : 'pettingzoo/atari/wizards_of_wor_v2.py', 'environment' : (wizard_of_wor_v2.raw_env())},
    'cooperative_pong' : { 'markdown': 'cooperative_pong.md', 'code' : 'pettingzoo/butterfly/cooperative_pong/cooperative_pong.py', 'environment' : (cooperative_pong_v3.env())},
    'knights_archers_zombies' : { 'markdown': 'knights_archers_zombies.md', 'code' : 'pettingzoo/butterfly/knights_archers_zombies/knights_archers_zombies.py', 'environment' : (knights_archers_zombies_v7.env())},
    'pistonball' : { 'markdown': 'pistonball.md', 'code' : 'pettingzoo/butterfly/pistonball/pistonball.py', 'environment' : (pistonball_v4.env())},
    'prison' : { 'markdown': 'prison.md', 'code' : 'pettingzoo/butterfly/prison/prison.py', 'environment' : (prison_v3.env())},
    'prospector' : { 'markdown': 'prospector.md', 'code' : 'pettingzoo/butterfly/prospector/prospector.py', 'environment' : (prospector_v4.env())},
    'backgammon' : { 'markdown': 'backgammon.md', 'code' : 'pettingzoo/classic/backgammon/backgammon.py', 'environment' : (backgammon_v3.env())},
    'checkers' : { 'markdown': 'checkers.md', 'code' : 'pettingzoo/classic/checkers/checkers.py', 'environment' : (checkers_v3.env())},
    'chess' : { 'markdown': 'chess.md', 'code' : 'pettingzoo/classic/chess/chess_env.py', 'environment' : (chess_v5.env())},
    'connect_four' : { 'markdown': 'connect_four.md', 'code' : 'pettingzoo/classic/connect_four/connect_four.py', 'environment' : (connect_four_v3.env())},
    'dou_dizhu' : { 'markdown': 'dou_dizhu.md', 'code' : 'pettingzoo/rlcard_envs/rlcard_envs/dou_dizhu.py', 'environment' : (dou_dizhu_v4.env())},
    'gin_rummy' : { 'markdown': 'gin_rummy.md', 'code' : 'pettingzoo/classic/rlcard_envs/gin_rummy.py', 'environment' : (gin_rummy_v4.env())},
    'go' : { 'markdown': 'go.md', 'code' : 'pettingzoo/classic/go/go.py', 'environment' : (go_v5.env())},
    'hanabi' : { 'markdown': 'hanabi.md', 'code' : 'pettingzoo/classic/hanabi/hanabi.py', 'environment' : (hanabi_v4.env())},
    'leduc_holdem' : { 'markdown': 'leduc_holdem.md', 'code' : 'pettingzoo/classic/rlcard_envs/leduc_holdem.py', 'environment' : (leduc_holdem_v4.env())},
    'mahjong' : { 'markdown': 'mahjong.md', 'code' : 'pettingzoo/classic/rlcard_envs/mahjong.py', 'environment' : (mahjong_v4.env())},
    'rps' : { 'markdown': 'rps.md', 'code' : 'pettingzoo/classic/rps/rps.py', 'environment' : (rps_v2.env())},
    'texas_holdem' : { 'markdown': 'texas_holdem.md', 'code' : 'pettingzoo/classic/rlcard_envs/texas_holdem.py', 'environment' : (texas_holdem_v4.env())},
    'texas_holdem_no_limit' : { 'markdown': 'texas_holdem_no_limit.md', 'code' : 'pettingzoo/classic/rlcard_envs/texas_holdem_no_limit.py', 'environment' : (texas_holdem_no_limit_v6.env())},
    'tictactoe' : { 'markdown': 'tictactoe.md', 'code' : 'pettingzoo/classic/tictactoe/tictactoe.py', 'environment' : (tictactoe_v3.env())},
    'uno' : { 'markdown': 'uno.md', 'code' : 'pettingzoo/classic/rlcard_envs/uno.py', 'environment' : (uno_v4.env())},
    'adversarial_pursuit' : { 'markdown': 'adversarial_pursuit.md', 'code' : 'pettingzoo/magent/adversarial_pursuit_v3.py', 'environment' : (adversarial_pursuit_v3.make_env())},
    'battle' : { 'markdown': 'battle.md', 'code' : 'pettingzoo/magent/battle_v3.py', 'environment' : (battle_v3.make_env())},
    'battlefield' : { 'markdown': 'battlefield.md', 'code' : 'pettingzoo/magent/battlefield_v3.py', 'environment' : (battlefield_v3.make_env())},
    'combined_arms' : { 'markdown': 'combined_arms.md', 'code' : 'pettingzoo/magent/combined_arms_v5.py', 'environment' : (combined_arms_v5.make_env())},
    'gather' : { 'markdown': 'gather.md', 'code' : 'pettingzoo/magent/gather_v3.py', 'environment' : (gather_v3.make_env())},
    'tiger_deer' : { 'markdown': 'tiger_deer.md', 'code' : 'pettingzoo/magent/tiger_deer_v3.py', 'environment' : (tiger_deer_v3.make_env())},
    'simple_adversary' : { 'markdown': 'simple_adversary.md', 'code' : 'pettingzoo/mpe/simple_adversary_v2.py', 'environment' : (simple_adversary_v2.make_env())},
    'simple_crypto' : { 'markdown': 'simple_crypto.md', 'code' : 'pettingzoo/mpe/simple_crypto.py', 'environment' : (simple_crypto_v2.make_env())},
    'simple_push' : { 'markdown': 'simple_push.md', 'code' : 'pettingzoo/mpe/simple_push_v2.py', 'environment' : (simple_push_v2.make_env())},
    'simple_reference' : { 'markdown': 'simple_reference.md', 'code' : 'pettingzoo/mpe/simple_reference_v2.py', 'environment' : (simple_reference_v2.make_env())},
    'simple_speaker_listener' : { 'markdown': 'simple_speaker_listener.md', 'code' : 'pettingzoo/mpe/simple_speaker_listener_v3.py', 'environment' : (simple_speaker_listener_v3.make_env())},
    'simple_spread' : { 'markdown': 'simple_spread.md', 'code' : 'pettingzoo/mpe/simple_spread_v2.py', 'environment' : (simple_spread_v2.make_env())},
    'simple_tag' : { 'markdown': 'simple_tag.md', 'code' : 'pettingzoo/mpe/simple_tag_v2.py', 'environment' : (simple_tag_v2.make_env())},
    'simple' : { 'markdown': 'simple.md', 'code' : 'pettingzoo/mpe/simple_v2.py', 'environment' : (simple_v2.make_env())},
    'simple_world_comm' : { 'markdown': 'simple_world_comm.md', 'code' : 'pettingzoo/mpe/simple_world_comm_v2.py', 'environment' : (simple_world_comm_v2.make_env())},
    'multiwalker' : { 'markdown': 'multiwalker.md', 'code' : 'pettingzoo/sisl/multiwalker/multiwalker.py', 'environment' : (multiwalker_v7.env())},
    'pursuit' : { 'markdown': 'pursuit.md', 'code' : 'pettingzoo/sisl/pursuit/pursuit.py', 'environment' : (pursuit_v4.env())},
    'waterworld' : { 'markdown': 'waterworld.md', 'code' : 'pettingzoo/sisl/waterworld/waterworld.py', 'environment' : (waterworld_v3.env())}
}
for file in files:

    file_content = [ line for line in open(files[file]['markdown']) ]
    code_file =  [ line for line in open(files[file]['code']) ]

    parameter_text = ""
    for line in code_file:
        search = re.search(":param (.+:)(.+)", line)
        if search:
            parameter_text = parameter_text + "`" + search.group(1) + "`" + search.group(2) + "\n"
    # Overwrite it
    writer = open(files[file]['markdown'],'w')

    frontmatter = False
    parameters = False
    write_params = True

    files[file]['environment'].reset()
    type = "continuous"
    if isinstance(files[file]['environment'].action_space(files[file]['environment'].agents[0]), gym.spaces.discrete.Discrete):
        type = "discrete"
    
    for line in file_content:
    # We search for the correct section
        if line.startswith("---"):
            frontmatter = not frontmatter
        if line.startswith("### Arguments"):
            parameters = True
            print("in")
        if frontmatter:
            if line.startswith("agents"):
                writer.write("agents: \"" + str(len(files[file]['environment'].agents)) + "\"\n")
            elif line.startswith("action-shape"):
                writer.write("action-shape: \"" + determine_act_shape(files[file]['environment']) + "\"\n")
            elif line.startswith("actions"):
                if type == "discrete":
                    writer.write("actions: " + "\"" + "Discrete" + "\"\n")
                else:
                    writer.write("actions: " + "\"" + "Box" + "\"\n")
            elif line.startswith("action-values"):
                if type == "discrete":
                    writer.write("action-values: \"" + determine_act_values(files[file]['environment']) + "\"\n")
                else:
                    writer.write("action-values: \"[" + re.search("\((.+)\)",determine_act_values(files[file]['environment'])).group(1) + "]\"\n")
            elif line.startswith("observation-shape"):
                writer.write("observation-shape: \"" + determine_obs_shape(files[file]['environment']) + "\"\n")
            elif line.startswith("observation-values"):
                writer.write("observation-values: \"" + determine_obs_values(files[file]['environment']) + "\"\n")
            elif line.startswith("state-shape"):
                writer.write("state-shape: \"" + determine_state_shape(files[file]['environment']) + "\"\n")
            elif line.startswith("state-values"):
                writer.write("state-values: \"" + determine_state_values(files[file]['environment']) + "\"\n")
            elif line.startswith("agent-labels"):
                writer.write("agent-labels: \"agents= " + str(files[file]['environment'].agents) + "\"\n")
            else:
                writer.write(line)
        elif parameters:
            if line.startswith("`") and not (line.startswith("```")) and (write_params):
                writer.write(parameter_text)
                write_params = False
            else:
                if line.startswith("#") and not write_params:
                    parameters = False
                elif not (line.startswith("`")) or (line.startswith("```")):
                    writer.write(line)
        else:
            writer.write(line)


    writer.close()