- Using "amplitude" encoded state space 
- Snake starts in random place with random direction each time
- Q table are dictionary, where keys are states and each values are Q values for each action

--------- God params 1 ----------
num_episodes = 100000, learning_rate = 0.0005, discount_rate = 0.95, max_exploration_rate = 1
min_exploration_rate = 0.001, exploration_decay_rate =  0.0005

--------- God params 2 ----------
num_episodes = 175000, learning_rate = 0.0005, discount_rate = 0.95, max_exploration_rate = 1
min_exploration_rate = 0.0001, exploration_decay_rate =  0.00005
