"""Uses `pickle` to save and restore populations (and other aspects of the simulation state)."""
from __future__ import print_function
from neat import Checkpointer

import os
import gzip
import random
import time

try:
    import cPickle as pickle # pylint: disable=import-error
except ImportError:
    import pickle # pylint: disable=import-error

from neat.population import Population
from neat.reporting import BaseReporter
from MyPlayer import MyPlayer, MyBrain


class AdvancedCheckpointer(Checkpointer):
    """
    A reporter class that performs checkpointing using `pickle`
    to save and restore populations (and other aspects of the simulation state).
    """
    def __init__(self, generation_interval=100, time_interval_seconds=300,
                 filename_prefix='neat-checkpoint-'):
      self.createPathIfNotExists(filename_prefix)
      super().__init__(generation_interval, time_interval_seconds, filename_prefix)
      print("~~~~~~~~~ AdvancedCheckpointer INITIALISED! ~~~~~~~~~")

    def createPathIfNotExists(self, filename):
      path = '/'.join(filename.split('/')[0:-1])
      isExist = os.path.exists(path)
      if not isExist:
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("Created checkpoint path:", path)

    def post_evaluate(self, config, population, species, best):
        # best will be none if none of the genomes in the population beat the global best
        if best != None: 
            self.save_best_genome(config, best, self.current_generation)

    def save_best_genome(self, config, best, generation):
        """ Save the current simulation state. """
        filename = '{0}{1}-best-genome'.format(self.filename_prefix, generation)
        print("Saving best genome yet to {0}".format(filename))
        # print("Best:")
        # print(best)

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (config, best, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def restore_best_genome(filename, color):
        """Restores a genome from a previous saved point."""
        with gzip.open(filename) as f:
            config, best, rndstate = pickle.load(f)
            random.setstate(rndstate)
            return (config, best)