from neat.graphs import feed_forward_layers
from neat.six_util import itervalues
from neat.nn.feed_forward import FeedForwardNetwork

from starNEAT.Lobe import Lobe
from starNEAT.LobeConfig import LobeConfig

class FeedForward(FeedForwardNetwork):
    def __init__(self, inputs, outputs, node_evals):
        super().__init__(inputs, outputs, node_evals)

    @staticmethod
    def create(lobe, lobe_config):
        """ Receives a sub-genome (a lobe) and returns its sub-phenotype (a Feed Forward Neural Network). """

        assert type(lobe) == Lobe
        assert type(lobe_config) == LobeConfig

        # Gather expressed connections.
        connections = [cg.key for cg in itervalues(lobe.connections) if cg.enabled]

        node_evals = []
        layers = feed_forward_layers(lobe_config.input_keys, lobe_config.output_keys, connections)
        for layer in layers:
            for node in layer:
                inputs = []
                for conn_key in connections:
                    inode, onode = conn_key
                    if onode == node:
                        cg = lobe.connections[conn_key]
                        inputs.append((inode, cg.weight))

                ng = lobe.nodes[node]
                aggregation_function = lobe_config.aggregation_function_defs.get(ng.aggregation)
                activation_function = lobe_config.activation_defs.get(ng.activation)
                node_evals.append((node, activation_function, aggregation_function, ng.bias, ng.response, inputs))

        return FeedForward(lobe_config.input_keys, lobe_config.output_keys, node_evals)


