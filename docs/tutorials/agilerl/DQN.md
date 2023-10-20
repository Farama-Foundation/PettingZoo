# AgileRL: Implementing DQN - Curriculum Learning and Self-play
This tutorial shows how to train a [DQN](https://agilerl.readthedocs.io/en/latest/api/algorithms/dqn.html) agent on the [connect four](https://pettingzoo.farama.org/environments/classic/connect_four/) classic environment.

This tutorial focuses on two techniques used in reinforcement learning - **curriculum learning** and **self-play**. Curriculum learning refers to training an agent on tasks of increasing difficulty in separate 'lessons'. Imagine you were trying to become a chess world champion. You would not decide to learn to play chess by immediately taking on a grand master - it would be too difficult. Instead, you would practice against people of the same ability as you, improve slowly, and increasingly play against harder opponents until you were ready to compete with the best. The same concept applies to reinforcement learning models. Sometimes, tasks are too difficult to learn in one go, and so we must create a curriculum to guide an agent and teach it to solve our ultimate hard environment.

This tutorial also uses self-play. Self-play is a technique used in competitive reinforcement learning environments. An agent trains by playing against a copy of itself - the opponent - and learns to beat this opponent. The opponent is then updated to a copy of this better version of the agent, and the agent must then learn to beat itself again. This is done repeatedly, and the agent iteratively improves by exploiting its own weaknesses and discovering new strategies.

In this tutorial, self-play is treated as the final lesson in the curriculum. However, these two techniques can be used independently of each other, and with unlimited resources, self-play can beat agents trained with human-crafted lessons through curriculum learning. [The Bitter Lesson](http://incompleteideas.net/IncIdeas/BitterLesson.html) by Richard Sutton provides an interesting take on curriculum learning and is definitely worth consideration from any engineer undertaking such a task. However, unlike Sutton, we do not all have the resources available to us that Deepmind and top institutions provide, and so one must be pragmatic when deciding how they will solve their own reinforcement learning problem. If you would like to discuss this exciting area of research further, please join the AgileRL [Discord server](https://discord.com/invite/eB8HyTA2ux) and let us know what you think!


## What is DQN?
[DQN](https://agilerl.readthedocs.io/en/latest/api/algorithms/dqn.html) (Deep Q-Network) is an extension of Q-learning that makes use of a replay buffer and target network to improve learning stability. For further information on DQN, check out the AgileRL [documentation](https://agilerl.readthedocs.io/en/latest/api/algorithms/dqn.html).

### Can I use it?

|   | Action Space | Observation Space |
|---|--------------|-------------------|
|Discrete  | ✔️           | ✔️                |
|Continuous   | ❌           | ✔️                |


## Environment Setup

To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/requirements.txt
   :language: text
```

## Code
### Curriculum learning and self-play using DQN on Connect Four
The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with AgileRL. If you have any questions, please feel free to ask in the [Discord server](https://discord.com/invite/eB8HyTA2ux).

This is a complicated tutorial, and so we will go through it in stages. The full code can be found at the end of this section.

First, we need to set up and modify our environment to enable curriculum learning. To do this, we create a ```CurriculumEnv``` class that acts as a wrapper on top of our Connect Four environment and enables us to alter the reward to guide the training of our agent. This uses configs that we can use to determine the lesson (more on these configs below).

```python
class CurriculumEnv:
    """Wrapper around environment to modify reward for curriculum learning.

    :param env: Environment to learn in
    :type env: PettingZoo-style environment
    :param lesson: Lesson settings for curriculum learning
    :type lesson: dict
    """
    def __init__(self, env, lesson):
        self.env = env
        self.lesson = lesson

    def fill_replay_buffer(self, memory):
        """Fill the replay buffer with experiences collected by taking random actions in the environment.

        :param memory: Experience replay buffer
        :type memory: AgileRL experience replay buffer
        """
        print("Filling replay buffer ...")
        while len(memory) < memory.memory_size:
            self.reset()  # Reset environment at start of episode
            observation, reward, done, truncation, _ = self.last()

            # Randomly decide whether agent will go first or second
            if random.random() > 0.5:
                opponent_first = False
            else:
                opponent_first = True

            p1_state, p1_state_flipped, p1_action, p1_next_state, p1_next_state_flipped = None, None, None, None, None
            done, truncation = False, False

            while not (done or truncation):
                # Player 0's turn
                p0_action_mask = observation["action_mask"]
                p0_state = np.moveaxis(observation["observation"], [-1], [-3])
                p0_state_flipped = np.expand_dims(np.flip(p0_state, 2), 0)
                p0_state = np.expand_dims(p0_state, 0)
                p0_action = self.env.action_space("player_0").sample(p0_action_mask)
                self.step(p0_action)  # Act in environment
                observation, env_reward, done, truncation, _ = self.last()
                p0_next_state = np.moveaxis(observation["observation"], [-1], [-3])
                p0_next_state_flipped = np.expand_dims(np.flip(p0_next_state, 2), 0)
                p0_next_state = np.expand_dims(p0_next_state, 0)

                if done or truncation:
                    reward = self.reward(done=True, player=0)
                    memory.save2memoryVectEnvs(
                        np.concatenate((p0_state, p1_state, p0_state_flipped, p1_state_flipped)),
                        [p0_action, p1_action, 6-p0_action, 6-p1_action],
                        [reward, LESSON["rewards"]["lose"], reward, LESSON["rewards"]["lose"]],
                        np.concatenate((p0_next_state, p1_next_state, p0_next_state_flipped, p1_next_state_flipped)),
                        [done, done, done, done],
                    )
                else:  # Play continues
                    if p1_state is not None:
                        reward = self.reward(done=False, player=0)
                        memory.save2memoryVectEnvs(
                            np.concatenate((p1_state, p1_state_flipped)),
                            [p1_action, 6-p1_action],
                            [reward, reward],
                            np.concatenate((p1_next_state, p1_next_state_flipped)),
                            [done, done],
                            )

                    # Player 1's turn
                    p1_action_mask = observation["action_mask"]
                    p1_state = np.moveaxis(observation["observation"], [-1], [-3])
                    p1_state[[0, 1], :, :] = p1_state[[0, 1], :, :]
                    p1_state_flipped = np.expand_dims(np.flip(p1_state, 2), 0)
                    p1_state = np.expand_dims(p1_state, 0)
                    p1_action = self.env.action_space("player_1").sample(p1_action_mask)
                    self.step(p1_action)  # Act in environment
                    observation, env_reward, done, truncation, _ = self.last()
                    p1_next_state = np.moveaxis(observation["observation"], [-1], [-3])
                    p1_next_state[[0, 1], :, :] = p1_next_state[[0, 1], :, :]
                    p1_next_state_flipped = np.expand_dims(np.flip(p1_next_state, 2), 0)
                    p1_next_state = np.expand_dims(p1_next_state, 0)

                    if done or truncation:
                        reward = self.reward(done=True, player=1)
                        memory.save2memoryVectEnvs(
                            np.concatenate((p0_state, p1_state, p0_state_flipped, p1_state_flipped)),
                            [p0_action, p1_action, 6-p0_action, 6-p1_action],
                            [LESSON["rewards"]["lose"], reward, LESSON["rewards"]["lose"], reward],
                            np.concatenate((p0_next_state, p1_next_state, p0_next_state_flipped, p1_next_state_flipped)),
                            [done, done, done, done],
                        )

                    else:  # Play continues
                        reward = self.reward(done=False, player=1)
                        memory.save2memoryVectEnvs(
                            np.concatenate((p0_state, p0_state_flipped)),
                            [p0_action, 6-p0_action],
                            [reward, reward],
                            np.concatenate((p0_next_state, p0_next_state_flipped)),
                            [done, done],
                        )
        print("Replay buffer warmed up.")
        return memory

    def check_winnable(self, lst, piece):
        """Checks if four pieces in a row represent a winnable opportunity, e.g. [1, 1, 1, 0] or [2, 0, 2, 2]

        :param lst: List of pieces in row
        :type lst: List
        :param piece: Player piece we are checking (1 or 2)
        :type piece: int
        """
        return lst.count(piece) == 3 and lst.count(0) == 1

    def check_vertical_win(self, player):
        """"Checks if a win is vertical.

        :param player: Player who we are checking, 0 or 1
        :type player: int
        """
        board = np.array(self.env.env.board).reshape(6, 7)
        piece = player + 1

        column_count = 7
        row_count = 6

        # Check vertical locations for win
        for c in range(column_count):
            for r in range(row_count - 3):
                if (
                    board[r][c] == piece
                    and board[r + 1][c] == piece
                    and board[r + 2][c] == piece
                    and board[r + 3][c] == piece
                ):
                    return True
        return False

    def check_three_in_row(self, player):
        """"Checks if there are three pieces in a row and a blank space next, or two pieces - blank - piece.

        :param player: Player who we are checking, 0 or 1
        :type player: int
        """
        board = np.array(self.env.env.board).reshape(6, 7)
        piece = player + 1

        # Check horizontal locations
        column_count = 7
        row_count = 6
        three_in_row_count = 0

        # Check vertical locations
        for c in range(column_count):
            for r in range(row_count - 3):
                if self.check_winnable(board[r:r+4, c].tolist(), piece):
                    three_in_row_count += 1

        # Check horizontal locations
        for r in range(row_count):
            for c in range(column_count - 3):
                if self.check_winnable(board[r, c:c+4].tolist(), piece):
                    three_in_row_count += 1

        # Check positively sloped diagonals
        for c in range(column_count - 3):
            for r in range(row_count - 3):
                if self.check_winnable([
                                        board[r, c],
                                        board[r+1, c+1],
                                        board[r+2, c+2],
                                        board[r+3, c+3]
                                       ], piece):
                    three_in_row_count += 1

        # Check negatively sloped diagonals
        for c in range(column_count - 3):
            for r in range(3, row_count):
                if self.check_winnable([
                                        board[r, c],
                                        board[r-1, c+1],
                                        board[r-2, c+2],
                                        board[r-3, c+3]
                                       ], piece):
                    three_in_row_count += 1

        return three_in_row_count

    def reward(self, done, player):
        """Processes and returns reward from environment according to lesson criteria.

        :param done: Environment has terminated
        :type done: bool
        :param player: Player who we are checking, 0 or 1
        :type player: int
        """
        if done:
            reward = self.lesson["rewards"]["vertical_win"] if self.check_vertical_win(player) else self.lesson["rewards"]["win"]
        else:
            agent_three_count = self.check_three_in_row(1-player)
            opp_three_count = self.check_three_in_row(player)
            if (agent_three_count + opp_three_count) == 0:
                reward = self.lesson["rewards"]["play_continues"]
            else:
                reward = self.lesson["rewards"]["three_in_row"] * agent_three_count + self.lesson["rewards"]["opp_three_in_row"] * opp_three_count
        return reward

    def last(self):
        """Wrapper around PettingZoo env last method"""
        return self.env.last()

    def step(self, action):
        """Wrapper around PettingZoo env step method"""
        self.env.step(action)

    def reset(self):
        """Wrapper around PettingZoo env reset method"""
        self.env.reset()
```


```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/agilerl_dqn_curriculum.py
   :language: python
```

### Watch the trained agents play
The following code allows you to load your saved MADDPG alogorithm from the previous training block, test the algorithms performance, and then visualise a number of episodes as a gif.
```{eval-rst}
.. literalinclude:: ../../../tutorials/AgileRL/render_agilerl_maddpg.py
   :language: python
```
