- Using "amplitude" encoded state space 
- Snake starts in random place with random direction each time
- Q table are dictionary, where keys are states and each values are Q values for each action
- Q table are update in game at each time step

settings (1):
BATCH_SIZE = 128
GAMMA = 0.999
EPS_START = 1.0
EPS_END = 0.001
EPS_DECAY = 0.00005
TARGET_UPDATE = 10
MY_SEED = 143
LR = 0.00005
MEMORY_SIZE = 10000