# starNEAT

## Disclaimer 
This project is an extension of [neat-python](https://neat-python.readthedocs.io/en/latest/#), as such, some of the original source-code was copied and modified to various degrees in the creation of this extension.

This project is for demonstrational & educational purposes only.

Official publication Citing:

    @misc{neat-python,  
        Title = {neat-python},  
        Author = {Alan McIntyre and Matt Kallada and Cesar G. Miguel and Carolina Feher da Silva},  
        howpublished = {\url{https://github.com/CodeReclaimers/neat-python}}   
    }

## What is starNEAT?
starNEAT an extension of the base NEAT (‘neat-python’) functionality, coined ‘starNEAT’. Where a traditional NEAT algorithm’s genome is the topology and internal values of a singular neural network which is often referred to as a brain, instead, the starNEAT algorithm’s genome consists of multiple, individually evolving neural networks referred to as ‘lobes’ (biologically, lobes are sections of the brain which each deal with a very specific function, e.g., vision, motor controls). These individual lobes (neural networks), made up the entire brain, the meaning behind ‘star’ in starNEAT, was referring to its particularly useful application of having a central lobe which would generally have a perspective of large contributing factors to decide which lobe within the brain to activate to make a decision. The algorithm supports all of the base functionality of a NEAT algorithm, such as speciation, stagnation, crossover, mutation, selection, etc., however, it has been expanded to support a dynamic number of lobes, each of which has the capacity to be assigned a specific fitness, as well as the entire brain genome, which can allow more advanced crossover procedures at the lobe-level.
 

In the case of Catan, a player is presented with many options of how to spend their turn, they could build a road, build a settlement, build a city, perform trades, buy/play a development card, and more, or even the option to end the player’s turn prematurely. In most cases, two primary decisions must be made, the first is, of these types of actions, based on the current observable game state, which should be played. Unless the action type was a single-choice option (e.g., to end a turn, or to buy a development card), there was still a decision to be made, this is where the rest of the lobes come into play. 
 

When utilising the starNEAT algorithm this particular way, the result of activating the first ‘central’ lobe (acting similarly to the stem of a brain), can enable a program to decide which specific lobe to activate next, for example, if the central lobe decided that the best option was to build a road, the lobe associated with that function would then be invoked, and is only provided the inputs necessary to make a decision regarding where to place the road, similarly, the outputs are restricted to road building actions. Alternatively, in situations (or even entire environments) where the available actions are restricted to a single action type, such as in the initial turns in the game of Catan, where the only option that the player has is to place a settlement, the ‘central’ lobe can be bypassed, the specific lobe can be individually invoked.  
