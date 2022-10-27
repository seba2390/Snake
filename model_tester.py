import matplotlib.pyplot as plt
import torch
from NeuralNet import *
import pygame
from pygame import *
import pygame
from pygame.locals import *
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from game import *

if __name__ == "__main__":

    # For reproducibility
    my_seed = 2876
    np.random.seed(my_seed)
    torch.manual_seed(my_seed)

    # Model
    test_agent = NeuralNetwork(seed=my_seed)
    model_path = "Models/score_46_model_63285.pt"
    test_agent.load_model(model_path)

    # Play
    theApp = SimpleSnakeApp(seed=my_seed,
                            neural_net=test_agent,
                            display_gameplay=True)
    theApp.on_execute()