import torch
import numpy as np

from NeuralNet import *


class Agent:
    def __init__(self, gamma: float, exploration_rate: float, lr: float, input_dims: list[int],
                 batch_size: int, nr_actions: int, max_mem_size: int = 10000,
                 exploration_rate_min: float = 0.01, exploration_decay_rate: float = 5e-4):
        self.gamma = gamma
        self.nr_actions = nr_actions
        self.exploration_rate = exploration_rate
        self.exploration_rate_min = exploration_rate_min
        self.exploration_decay_rate = exploration_decay_rate
        self.lr = lr

        self.input_dims = input_dims
        self.action_space = [action for action in range(self.nr_actions)]

        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_counter = 0

        self.Q_eval = DeepQNetwork(lr=self.lr, nr_actions=self.nr_actions,
                                   input_dims=self.input_dims, fc1_dims=128,
                                   fc2_dims=256)

        self.device = self.Q_eval.device

        self.state_memory = torch.zeros(size=(self.mem_size, *self.input_dims),
                                        dtype=torch.float32,
                                        device=self.device)
        self.new_state_memory = torch.zeros(size=(self.mem_size, *self.input_dims),
                                            dtype=torch.float32,
                                            device=self.device)
        self.action_memory = torch.zeros(size=(self.mem_size,),
                                         dtype=torch.long,
                                         device=self.device)
        self.reward_memory = torch.zeros(size=(self.mem_size,),
                                         dtype=torch.float32,
                                         device=self.device)
        self.terminal_memory = torch.zeros(size=(self.mem_size,),
                                           dtype=torch.bool,
                                           device=self.device)

    def store_transition(self, state, action, reward, new_state, done_flag: bool):
        """ note that:
        0%3 = 0, 1%3 = 1, 2%3 = 2,
        3%3 = 0, 4%3 = 1, 5%3 = 2 ... """
        index = self.mem_counter % self.mem_size

        # Storing transition in memory
        self.state_memory[index] = state
        self.new_state_memory[index] = new_state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.terminal_memory[index] = done_flag

        # Iteration index counter
        self.mem_counter += 1

    def choose_action(self, observation):
        assert type(observation) is torch.Tensor, f'Observation should be torch tensor but is: {type(observation)}.'
        if torch.rand(1).item() > self.exploration_rate:
            # Exploitation (relying on Q value)
            actions = self.Q_eval.forward(observation)
            best_action = torch.argmax(actions).item()
            return best_action
        else:
            # Exploration (random action)
            rng_index = torch.randint(low=0, high=self.nr_actions, size=(1,)).item()
            random_action = self.action_space[rng_index]
            return random_action

    def learn(self):
        """ Memory initially filled w. zeros
        - first beginning learning process when
        non-zero memory is at least batch_size. """
        if self.mem_counter < self.batch_size:
            return None

        # Clearing gradient buffer
        self.Q_eval.optimizer.zero_grad()

        # Max index to sample from memory (to avoid sampling 0)
        max_memory_index = min(self.mem_counter, self.mem_size)

        # Unique indices
        batch_indices = np.random.choice(a=max_memory_index,
                                         size=self.batch_size,
                                         replace=False)

        # Getting memory samples
        state_batch = self.state_memory[batch_indices]
        new_state_batch = self.new_state_memory[batch_indices]
        reward_batch = self.reward_memory[batch_indices]
        terminal_batch = self.terminal_memory[batch_indices]
        action_batch = self.action_memory[batch_indices]

        #print("action_batch:", action_batch)

        #print("State batch shape: ", state_batch.shape)
        # Calculating Q values
        q_eval = self.Q_eval.forward(state_batch)[torch.arange(self.batch_size, dtype=torch.long), action_batch]
        #print("q_eval  shape: ", q_eval.shape)
        q_next = self.Q_eval.forward(new_state_batch)
        #print("q_next  shape: ", q_next.shape)
        q_next[terminal_batch] = 0.0
        q_target = reward_batch + self.gamma * torch.max(q_next, dim=1)[0]
        #print("q_target  shape: ", q_target.shape)

        # Calculating loss
        loss = self.Q_eval.loss(target=q_target,
                                prediction=q_eval)
        # Performing backpropagation (torch calculates gradient)
        loss.backward()

        # Takes gradient step and updating network params
        self.Q_eval.optimizer.step()

        # Updating exploration rate
        if self.exploration_rate > self.exploration_rate_min:
            self.exploration_rate -= self.exploration_decay_rate
        else:
            self.exploration_rate = self.exploration_rate_min
