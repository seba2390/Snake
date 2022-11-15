import matplotlib.pyplot as plt
import torch
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from game import *


if __name__ == "__main__":

    # for reproducibility
    my_seed = 2786
    np.random.seed(my_seed)
    torch.manual_seed(my_seed)

    # Creating The Q-Table
    action_space_size = 4  # Up-left-down-right
    state_space_size = 2**12 # All possible permutations of bitstring og length 12
    print("action_space_size: ", action_space_size)
    print("state_space_size: ", state_space_size)
    q_table = np.zeros((state_space_size, action_space_size))
    print("Q table size: ", q_table.shape)

    # View good score games while training ?
    view_games = True

    # Stats for plotting
    loss_means = []
    highest_scores = []
    best_play_models = []

    # Initializing Q-Learning Parameters
    num_episodes = 1000
    max_steps_per_episode = 1000000

    learning_rate = 0.075
    discount_rate = 0.99

    exploration_rate = 1  # Initially exploring (all q-table vals = 0 at beginning)
    max_exploration_rate = 1
    min_exploration_rate = 0.01
    exploration_decay_rate = 0.005

    # The Q-Learning Algorithm Training Loop
    rewards_all_episodes = []
    action_map = {"up": 0, "down": 1, "left": 2, "right": 3}
    for episode in tqdm(range(num_episodes)):
        agent = SimpleSnakeApp(seed=my_seed,
                               Q_table=q_table,
                               display_gameplay=False)

        done = False
        rewards_current_episode = 0
        my_random_flag = False
        for step in range(max_steps_per_episode):

            # Exploration-exploitation trade-off
            exploration_rate_threshold = np.random.uniform(0, 1)
            if exploration_rate_threshold > exploration_rate:
                my_random_flag = True
            else:
                my_random_flag = False

            # Take new action
            reward, running, action, _state, new_state = agent.step(my_random_flag)
            _state = int(tensor_2_string(_state), 2)
            new_state = int(tensor_2_string(new_state), 2)
            action = action_map[action]
            done = not running

            # Update Q-table (using Bellman equation for Optimal Q-value function)
            q_table[_state, action] = q_table[_state, action] * (1 - learning_rate) + learning_rate * (
                        reward + discount_rate * np.max(q_table[new_state, :]))

            # Add new reward
            rewards_current_episode += reward

            if done:
                break

        # Exploration rate decay
        exploration_rate = min_exploration_rate + (max_exploration_rate - min_exploration_rate) * np.exp(
            -exploration_decay_rate * episode)

        # Add current episode reward to total rewards list
        rewards_all_episodes.append(rewards_current_episode)

    # Calculating average over 100's of episodes
    batch_size = 1
    avg_rewards = []
    for batch in range(int(num_episodes/batch_size)):
        avg_rewards.append(np.mean(rewards_all_episodes[batch_size * batch : batch_size * (batch + 1)]))

    # Plot reward of each 'episode'
    fig, ax = plt.subplots(1,1,figsize=(5,3))
    ax.plot(list(range(1,len(rewards_all_episodes)+1)), rewards_all_episodes)
    plt.show()