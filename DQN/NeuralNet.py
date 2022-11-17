import torch


class DeepQNetwork(torch.nn.Module):
    def __init__(self, lr: float, input_dims: list[int], fc1_dims: int,
                 fc2_dims: int, nr_actions: int, seed: int = 0):
        super(DeepQNetwork, self).__init__()

        self.seed = seed  # For rng reproducibility
        torch.manual_seed(self.seed)

        self.lr = lr
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.nr_actions = nr_actions

        self.fc = torch.nn.Sequential(torch.nn.Linear(in_features=self.input_dims[0], out_features=self.fc1_dims),
                                      torch.nn.ReLU(),
                                      torch.nn.Linear(in_features=self.fc1_dims, out_features=self.fc2_dims),
                                      torch.nn.ReLU(),
                                      torch.nn.Linear(in_features=self.fc2_dims, out_features=self.nr_actions))

        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        self.loss_func = torch.nn.MSELoss()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    def forward(self, state):
        actions = self.fc(state)
        return actions

    def loss(self, target, prediction):
        return self.loss_func(target, prediction)

