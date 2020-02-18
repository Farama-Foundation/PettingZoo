from gym.envs.registration import register

register(
	id='ChessVsRandomBot-v0',
	entry_point='gym_chess.envs:ChessEnv',
	kwargs={'opponent' : 'random'},
)

register(
	id='ChessVsSelf-v0',
	entry_point='gym_chess.envs:ChessEnv',
	kwargs={'opponent' : 'none'},
	# max_episode_steps=100,
	# reward_threshold=.0, # optimum = .0
)