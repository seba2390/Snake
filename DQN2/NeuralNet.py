import torch


class DeepQNetwork(torch.nn.Module):
    def __init__(self, lr: float, input_dims: tuple[int, int],
                 nr_actions: int, nr_consecutive_frames: int = 1, seed: int = 0):
        super(DeepQNetwork, self).__init__()

        self.seed = seed  # For rng reproducibility
        torch.manual_seed(self.seed)

        self.lr = lr
        self.input_dims = input_dims
        self.nr_actions = nr_actions
        self.nr_consecutive_frames = nr_consecutive_frames

        def conv2d_size_out(size, kernel_size, stride):
            """Calculating output size of conv layer"""
            return (size - (kernel_size - 1) - 1) // stride + 1

        # ----------- Defining Layers in Neural Net ------------ #
        self.conv1 = torch.nn.Conv2d(in_channels=self.nr_consecutive_frames, out_channels=32, kernel_size=8, stride=4)
        self.conv2 = torch.nn.Conv2d(in_channels=self.conv1.out_channels, out_channels=64, kernel_size=4, stride=2)
        self.conv3 = torch.nn.Conv2d(in_channels=self.conv2.out_channels, out_channels=64, kernel_size=3, stride=1)

        h1 = conv2d_size_out(self.input_dims[0], self.conv1.kernel_size[0], self.conv1.stride[0])
        w1 = conv2d_size_out(self.input_dims[0], self.conv1.kernel_size[1], self.conv1.stride[1])
        h2 = conv2d_size_out(h1, self.conv2.kernel_size[0], self.conv2.stride[0])
        w2 = conv2d_size_out(w1, self.conv2.kernel_size[1], self.conv2.stride[1])
        h3 = conv2d_size_out(h2, self.conv3.kernel_size[0], self.conv3.stride[0])
        w3 = conv2d_size_out(w2, self.conv3.kernel_size[1], self.conv3.stride[1])

        flattened_size = h3 * w3 * self.conv3.out_channels
        self.lin1 = torch.nn.Linear(in_features=flattened_size, out_features=512)
        self.lin2 = torch.nn.Linear(in_features=self.lin1.out_features, out_features=self.nr_actions)

        self.rectifier = torch.nn.ReLU()

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        state = state.to(self.device)
        state = self.rectifier(self.conv1(state))
        state = self.rectifier(self.conv2(state))
        state = self.rectifier(self.conv3(state))
        state = torch.flatten(input=state,start_dim=1)
        state = self.lin1(state)
        state = self.lin2(state)
        return state
