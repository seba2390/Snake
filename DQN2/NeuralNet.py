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


class DQN(torch.nn.Module):

    def __init__(self, h, w, outputs, seed: int = 0):
        super(DQN, self).__init__()

        self.seed = seed  # For rng reproducibility
        torch.manual_seed(self.seed)

        self.conv1 = torch.nn.Conv2d(3, 16, kernel_size=5, stride=2)
        self.bn1 = torch.nn.BatchNorm2d(16)
        self.conv2 = torch.nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = torch.nn.BatchNorm2d(32)
        self.conv3 = torch.nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = torch.nn.BatchNorm2d(32)

        # Number of Linear input connections depends on output of conv2d layers
        # and therefore the input image size, so compute it.
        def conv2d_size_out(size, kernel_size = 5, stride = 2):
            return (size - (kernel_size - 1) - 1) // stride  + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(w)))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(h)))
        linear_input_size = convw * convh * 32
        self.head = torch.nn.Linear(linear_input_size, outputs)

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = x.to(self.device)
        x = torch.nn.functional.relu(self.bn1(self.conv1(x)))
        x = torch.nn.functional.relu(self.bn2(self.conv2(x)))
        x = torch.nn.functional.relu(self.bn3(self.conv3(x)))
        return self.head(x.view(x.size(0), -1))