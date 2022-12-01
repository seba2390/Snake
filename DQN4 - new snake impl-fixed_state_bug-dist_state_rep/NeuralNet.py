import torch


class DeepQNetwork(torch.nn.Module):
    def __init__(self, lr: float, input_size: int,
                 nr_actions: int, seed: int = 0):
        super(DeepQNetwork, self).__init__()

        self.seed = seed  # For rng reproducibility
        torch.manual_seed(self.seed)

        self.lr = lr
        self.input_size = input_size
        self.nr_actions = nr_actions

        # ----------- Defining Layers in Neural Net ------------ #
        self.lin1 = torch.nn.Linear(in_features=self.input_size, out_features=self.input_size*30)
        self.lin2 = torch.nn.Linear(in_features=self.input_size*30, out_features=self.input_size*15)
        self.lin3 = torch.nn.Linear(in_features=self.input_size*15, out_features=self.nr_actions)
        self.rectifier1 = torch.nn.ReLU()

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        state = state.to(self.device)
        state = self.rectifier1(self.lin1(state))
        state = self.rectifier1(self.lin2(state))
        state = self.lin3(state)
        return state
