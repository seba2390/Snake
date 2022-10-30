import numpy as np
import torch
import torchvision
from tqdm import tqdm
import matplotlib.pyplot as plt
import wandb
import os
import scipy


class NeuralNetwork(torch.nn.Module):
    def __init__(self, seed):
        super(NeuralNetwork, self).__init__()

        self.seed = seed
        torch.random.manual_seed(self.seed)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.state_space_size = 12
        self.action_space_size = 4
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.state_space_size,
                            out_features=13 * self.state_space_size),
            torch.nn.ReLU(),
            torch.nn.Linear(in_features=13 * self.state_space_size,
                            out_features=self.action_space_size),
            )

    def forward(self, X):
        return self.fc(X)

    def save_model(self, score, seed):
        torch.save(obj=self.state_dict(), f="Models/score_"+str(score)+"_model_seed_"+str(seed)+".pt")

    def load_model(self, path):
        self.load_state_dict(torch.load(path))



