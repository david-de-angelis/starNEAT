#from catanatron import Game, RandomPlayer, Color

from catanatron.game import Game, Color, Action, Player
from catanatron.models.player import RandomPlayer
from my_player import MyPlayer

arr = []
for i in range (1000):
  # Play a simple 4v4 game
  players = [
      RandomPlayer(Color.RED),
      RandomPlayer(Color.BLUE),
      #RandomPlayer(Color.WHITE),
      MyPlayer(Color.ORANGE, {})
  ]
  game = Game(players)
  arr.append(game.play())
  #print(arr[i])  # returns winning color

r,b,w,o = 0,0,0,0

for i in range(len(arr)):
  if arr[i] == Color.RED:
    r += 1
  elif arr[i] == Color.BLUE:
    b += 1
  elif arr[i] == Color.WHITE:
    w += 1
  elif arr[i] == Color.ORANGE:
    o += 1
  else:
    print("Other:", arr[i])

print("Red: ", r)
print("Blue: ", b)
print("White: ", w)
print("Orange: ", o)
