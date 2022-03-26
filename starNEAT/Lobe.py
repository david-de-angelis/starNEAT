import string
from neat import DefaultGenome
from neat.six_util import iteritems, iterkeys

class Lobe(DefaultGenome):
  
    def __init__(self, name, connections, nodes):
      assert type(name) == str

      self.key = name
      self.name = name
      self.connections = connections if connections != None else {}
      self.nodes = nodes if nodes != None else {}
      self.fitness = None