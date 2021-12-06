from pettingzoo.butterfly import prospector_v4
import numpy as np
import re

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

def determine_obs_value (file):
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

def determine_act_value (file):
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

def determine_state_value (file):
    values = []
    if (file.state_space.shape) == ():
        if (file.state_space) not in values:
            values.append(file.state_space)
    else:
        if (np.amin(file.state_space.low), np.amax(file.state_space.high)) not in values:
            values.append((np.amin(file.state_space.low), np.amax(file.state_space.high)))
    return create_string(values)

# Load the file into file_content
files = {'c4' : { 'markdown': 'test.md', 'code' : 'pettingzoo/butterfly/prospector/prospector.py', 'environment' : (prospector_v4.env())}}
for file in files:

    file_content = [ line for line in open(files[file]['markdown']) ]
    code_file =  [ line for line in open(files[file]['code']) ]

    parameter_text = ""
    for line in code_file:
        if bool(re.match("`.+`:", line)):
            parameter_text = parameter_text + line + "\n" + "\n"
    # Overwrite it
    writer = open(files[file]['markdown'],'w')

    frontmatter = False
    parameters = False

    files[file]['environment'].reset()
    for line in file_content:
    # We search for the correct section
        if line.startswith("---"):
            frontmatter = not frontmatter
        if line.startswith("### Arguments"):
            parameters = True
        if frontmatter:
            if line.startswith("agents"):
                writer.write("agents: \"" + str(len(files[file]['environment'].agents)) + "\"\n")
            elif line.startswith("action-shape"):
                writer.write("action-shape: \"" + determine_act_shape(files[file]['environment']) + "\"\n")
            elif line.startswith("action-values"):
                writer.write("action-values: \"" + determine_act_value(files[file]['environment']) + "\"\n")
            elif line.startswith("observation-shape"):
                writer.write("observation-shape: \"" + determine_obs_shape(files[file]['environment']) + "\"\n")
            elif line.startswith("observation-values"):
                writer.write("observation-values: \"" + determine_obs_value(files[file]['environment']) + "\"\n")
            elif line.startswith("state-shape"):
                writer.write("state-shape: \"" + determine_state_shape(files[file]['environment']) + "\"\n")
            elif line.startswith("state-values"):
                writer.write("state-values: \"" + determine_state_value(files[file]['environment']) + "\"\n")
            elif line.startswith("agent-labels"):
                writer.write("agent-labels: \"agents= " + str(files[file]['environment'].agents) + "\"\n")
            else:
                writer.write(line)
        elif parameters:
            if line.startswith("#"):
                writer.write(parameter_text)
                writer.write(line)
                parameters = False
        else:
            writer.write(line)


    writer.close()