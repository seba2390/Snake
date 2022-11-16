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


    # Model
    test_agent = NeuralNetwork(seed=0)
    model_path = "Models/score_56_model_seed_4338.pt"
    test_agent.load_model(model_path)

    # Play
    theApp = SimpleSnakeApp(seed=4338,
                            neural_net=test_agent,
                            display_gameplay=True)
    theApp.on_execute()