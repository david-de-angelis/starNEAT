from neat.config import ConfigParameter
from neat.genome import DefaultGenomeConfig

from starNEAT.LobeConfig import LobeConfig

class BrainGenomeConfig(DefaultGenomeConfig):

    def __init__(self, params):
        super().__init__(params) # do i even need to do this? #not after full lobe implementation

        brain_lobes_metadata = ConfigParameter('brain_lobes', list)
        setattr(self, brain_lobes_metadata.name, brain_lobes_metadata.interpret(params))

        self.brain_lobes_config = {}
        for lobe_name in self.brain_lobes:
            lobeConfig = LobeConfig(lobe_name, params)
            self.brain_lobes_config[lobe_name] = lobeConfig
