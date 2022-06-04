from __future__ import print_function
from catanatron.game import Color, Game
from catanatron.models.player import RandomPlayer
from catanatron.players.weighted_random import WeightedRandomPlayer
from catanatron.players.search import VictoryPointPlayer
from opponents.mcts import MCTSPlayer
from MyPlayer import MyPlayer, MyBrain
from starNEAT.starNEAT import starNEAT
from opponents.minimax import AlphaBetaPlayer, ValueFunctionPlayer
from opponents.playouts import GreedyPlayoutsPlayer
from reporters.AdvancedCheckpointer import AdvancedCheckpointer
import time
import random


colors = [Color.BLUE, Color.RED, Color.WHITE, Color.ORANGE]

start = time.time()
num_games = 10
for i in range(num_games):
  random.shuffle(colors)

  opponent1 = AlphaBetaPlayer(colors[0])
  opponent2 = AlphaBetaPlayer(colors[1])

  players = [ opponent1, opponent2 ]
  random.shuffle(players)

  game = Game(players)
  winning_color = game.play()

end = time.time()
print(type(opponent1))
time_took = end-start
print(time_took, "for", num_games, "games")