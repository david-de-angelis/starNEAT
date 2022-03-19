from neat import DefaultGenome

class Lobe(DefaultGenome):
  
  def __init__(self, name, connections = {}, nodes = {}):
    self.name = name
    self.connections = connections
    self.nodes = nodes