
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Provide 1 argument")
    arg = sys.argv[1]
    
    game_list = [
                 "cooperative_pong", 
                 "piston_ball", 
                 "pursuit", 
                 "waterworld", 
                 "multi_walker",
                 "pursuit_sa", 
                ]
    if arg not in game_list:
        raise Exception("Input a valid game. Choose from {}".format(game_list))
        
    if arg == "cooperative_pong":
        import gamma_games.cooperative_pong.test
    
    if arg == "piston_ball":
        import gamma_games.piston_ball.test

    if arg == "pursuit":
        import sisl_games.pursuit.test
    
    if arg == "waterworld":
        import sisl_games.waterworld.test
    
    if arg == "multi_walker":
        import sisl_games.multi_walker.test

    if arg == "pursuit_sa":
        import sisl_games.pursuit_single_action.test
