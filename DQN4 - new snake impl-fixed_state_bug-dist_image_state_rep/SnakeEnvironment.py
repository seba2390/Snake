import torch

from Util import *
from GameObjects import *
import numpy as np
import torchvision.transforms.functional as fn

class SnakeEnvironment:
    def __init__(self, seed, neural_net=None, display_gameplay: bool = True, graphics_speed: int = 1):

        # For RNG reproducibility
        np.random.seed(seed)

        # Occasional Neural Net for directing snake
        if neural_net is not None:
            self.neural_net = neural_net
        else:
            self.neural_net = None

        # Tracking variables
        self.current_reward = 0
        self.loss = 0
        self.break_out_counter = 0
        self.current_score = 0
        self.max_iteration_token = 0

        # Settings
        self.max_iterations = 2000
        self.display_gameplay = display_gameplay
        self.graphics_speed = graphics_speed  # chose 1,2,3,4,5,6,7
        self.apple_reward = 2.0
        self.death_punishment = -2.0
        self.closer_2_apple_reward = 0.5 * self.apple_reward / self.max_iterations
        self.longer_from_apple_punishment = - 0.5 * self.apple_reward / self.max_iterations
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 30, 30
        self.apple_block_size = self.apple_block_width, self.apple_block_height = 30, 30
        self.screen_size = self.screen_width, self.screen_height = 600,600
        self.snake_speed = self.snake_block_width  # pixels pr. frame

        if self.display_gameplay:
            self.running = True
            self.display_surf = None
            self.background_surf = None
            self.fps = pygame.time.Clock()
            self.score_text, self.score_value_text = None, None

        self.snake_block_surf = None
        self.snake_block_rect = None

        self.apple_block_surf = None
        self.apple_block_rect = None

        self._initialize()

        # In game constants
        self.max_dist = np.sqrt(
            (self.screen_width - self.snake_block_width) ** 2 + (self.screen_height - self.snake_block_height) ** 2)

        self.snake = Snake(rect=self.snake_block_rect,
                           screen_size=self.screen_size[0],
                           seed=seed)
        self.apple = Apple(rect=self.apple_block_rect,
                           screen_size=self.screen_size[0],
                           seed=seed)

    # ---- PRIVATE ---- #
    def __str__(self):
        str_repr =   "####### Environment settings ####### : \n" \
                   + "screen_size: " + str(self.__dict__["screen_size"]) + "\n" \
                   + "snake_block_size: " + str(self.__dict__["snake_block_size"]) + "\n" \
                   + "grid_size: " + str(self.__dict__["screen_size"][0]//self.__dict__["snake_block_size"][0]) + "\n" \
                   + "apple_reward: " + str(self.__dict__["apple_reward"]) + "\n" \
                   + "death_punishment: " + str(self.__dict__["death_punishment"]) + "\n" \
                   + "closer_2_apple_reward: " + str(self.__dict__["closer_2_apple_reward"]) + "\n" \
                   + "longer_from_apple_punishment: " + str(self.__dict__["longer_from_apple_punishment"]) + "\n" \
                   + "max_iterations: " + str(self.__dict__["max_iterations"]) + "\n\n"
        return str_repr

    def _initialize(self):
        self.running = True
        # Initializing pygame and loading in graphics for background
        if self.display_gameplay:
            pygame.init()
            pygame.font.init()
            self.display_surf = pygame.display.set_mode(size=self.screen_size,
                                                        flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
            self.background_surf = pygame.image.load("media/background.png").convert()
            # Loading in graphics for snake
            self.snake_block_surf = pygame.image.load("media/snake_block.png").convert_alpha()
            self.snake_block_rect = self.snake_block_surf.get_rect()
            # Loading in graphics for apple
            self.apple_block_surf = pygame.image.load("media/apple_block.png").convert_alpha()
            self.apple_block_rect = self.snake_block_surf.get_rect()
            # loading in graphics for text objects
            font_filename = "media/font.ttf"
            self.score_text = PygameText(filename=font_filename, text="score: ", text_size=25)
            self.score_text.set_position(left=30, top=5)
            self.score_value_text = PygameText(filename=font_filename, text=str(self.current_score), text_size=25)
            self.score_value_text.set_position(left=self.score_text.rect.right + 20, top=5)
        # Using fake rects instead of graphics
        else:
            self.snake_block_rect = FakeRect(width=self.snake_block_width, height=self.snake_block_height)
            self.apple_block_rect = FakeRect(width=self.apple_block_width, height=self.apple_block_height)

    def _set_snake_direction(self, direction: int) -> None:
        int_2_direction = {0: "right", 1: "left", 2: "up", 3: "down"}
        direction = int_2_direction[direction]
        if direction == "right" and self.snake.get_direction() != "left":
            self.snake.set_direction("right")
        elif direction == "left" and self.snake.get_direction() != "right":
            self.snake.set_direction("left")
        elif direction == "up" and self.snake.get_direction() != "down":
            self.snake.set_direction("up")
        elif direction == "down" and self.snake.get_direction() != "up":
            self.snake.set_direction("down")

    def _update_direction(self, direction: int = 42, event=None) -> None:
        # Checking for closed window
        if event is not None:
            if event.type == pygame.QUIT:
                self.running = False
                return None
        else:
            # If no neural net is given - user control is enabled
            if self.neural_net is None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT and self.snake.get_direction() != "left":
                        self.snake.set_direction("right")
                    elif event.key == pygame.K_LEFT and self.snake.get_direction() != "right":
                        self.snake.set_direction("left")
                    elif event.key == pygame.K_UP and self.snake.get_direction() != "down":
                        self.snake.set_direction("up")
                    elif event.key == pygame.K_DOWN and self.snake.get_direction() != "up":
                        self.snake.set_direction("down")
            # If neural net is given - directions is given by neural net
            else:
                self._set_snake_direction(direction=direction)

    def _update_score(self):
        """ Function for updating score when apple is found. """
        self.current_score += 1
        self.loss += self.apple_reward
        self.current_reward += self.apple_reward
        if self.display_gameplay:
            current_x, current_y = self.score_value_text.rect.centerx, self.score_value_text.rect.centery
            self.score_value_text.surface = self.score_value_text.font.render(str(self.current_score), True,
                                                                              self.score_value_text.color, None)
            self.score_value_text.rect = self.score_value_text.surface.get_rect()
            self.score_value_text.rect.centerx, self.score_value_text.rect.centery = current_x, current_y

    def _in_game_render(self):
        """ Function for updating screen w. graphics."""
        if self.display_gameplay:
            # Rendering background
            self.display_surf.blit(self.background_surf, (0, 0))
            # Rendering snake
            for block in range(self.snake.snake_length):
                self.display_surf.blit(self.snake_block_surf, self.snake._snake_blocks[block].rect)
            # Rendering apple
            self.display_surf.blit(self.apple_block_surf, self.apple.apple_block.rect)
            # Rendering score text
            self.display_surf.blit(self.score_text.surface, self.score_text.rect)
            # Rendering score value
            self.display_surf.blit(self.score_value_text.surface, self.score_value_text.rect)
            self.fps.tick(self.graphics_speed * 10)

            pygame.display.flip()  # This is needed for image to show up ??

    def _close_window(self):
        if self.display_gameplay:
            pygame.quit()

    def _distance_2_apple(self) -> float:
        head_x, head_y = self.snake.get_head().centerx, self.snake.get_head().centery
        apple_x, apple_y = self.apple.get_apple().centerx, self.apple.get_apple().centery
        return np.linalg.norm(np.array([head_x, head_y]) - np.array([apple_x, apple_y]))

    def _distance_2_tail(self) -> float:
        head_x, head_y = self.snake.get_head().centerx, self.snake.get_head().centery
        tail_x, tail_y = self.snake.get_tail().centerx, self.snake.get_tail().centery
        return np.linalg.norm(np.array([head_x, head_y]) - np.array([tail_x, tail_y]))

    # ---- PUBLIC ---- #
    def get_state(self):
        screen_size = self.screen_width
        grid = torch.zeros(size=(screen_size, screen_size), dtype=torch.float32)

        # Setting boundaries
        #grid[0] = grid[grid_size + 1] = grid[:, 0] = grid[:, grid_size + 1] = 1

        # Placing head
        head = self.snake.get_head()
        head_x = head.left #// self.snake_block_width
        head_y = head.top #// self.snake_block_width
        for i in range(self.screen_width // self.snake_block_width):
            for j in range(self.screen_width // self.snake_block_width):
                grid[head_y + i][head_x + j] = 0.75

        # Placing body
        for body_idx in range(1, self.snake.snake_length):
            body = self.snake.get_body(index=body_idx)
            body_x = body.left #// self.snake_block_width
            body_y = body.top #// self.snake_block_width
            for i in range(self.screen_width // self.snake_block_width):
                for j in range(self.screen_width // self.snake_block_width):
                    grid[body_y + i][body_x + j] = 0.75/2.0

        # Placing apple
        apple = self.apple.get_apple()
        apple_x = apple.left #// self.apple_block_width
        apple_y = apple.top #// self.apple_block_width
        for i in range(self.screen_width // self.snake_block_width):
            for j in range(self.screen_width // self.snake_block_width):
                grid[apple_y + i][apple_x + j] = 1
        grid = fn.resize(img=grid.resize_(1,1,self.screen_width,self.screen_width), size=[84])
        return grid

    def run(self):
        # Spawning snake head (random)
        self.snake.initialize()
        # Spawning apple in remaining available space (random)
        self.apple.initialize(grid=self.snake.get_grid())
        # Main loop
        while self.running:
            # Rendering screen
            self._in_game_render()
            # Directing snake according either to neural net or user input
            if self.neural_net is None:
                for _event in pygame.event.get():
                    if self.neural_net is None:
                        self._update_direction(event=_event)
            else:
                current_action_index = torch.argmax(input=self.neural_net.forward(self.get_state())).item()
                self._update_direction(direction=current_action_index)

            # Updating snake state
            self.snake.update(velocity=self.snake_speed)
            # If snake has not hit itself or walls
            if not self.snake.dead:
                # Checking whether snake has found apple
                if self.snake.found_apple(apple=self.apple):
                    self._update_score()
                    self.break_out_counter = 0
            else:
                self.running = False
                break
            # Checking that snake hasn't just started looping around
            if self.break_out_counter == self.max_iterations:
                self.running = False
            # Iterating counter that checks for looping snake
            else:
                self.break_out_counter += 1
        self._close_window()

    def initialize_environment(self):
        """ Wrapper for spawning snake head
        and apple block."""

        # Setting game flag
        self.running = True
        # Spawning snake head (random)
        self.snake.initialize()
        # Spawning apple in remaining available space (random)
        self.apple.initialize(grid=self.snake.get_grid())

    def step(self, action: int):
        """ Function for stepping in environment."""
        self.current_reward = 0
        # Setting snake direction
        self._set_snake_direction(direction=action)
        # Calculating initial distance to apple
        s_0_dist = self._distance_2_apple()
        # Updating snake state
        self.snake.update(velocity=self.snake_speed)
        # Calculating final distance to apple
        s_1_dist = self._distance_2_apple()

        if s_1_dist < s_0_dist:
            self.current_reward += self.closer_2_apple_reward
        else:
            self.current_reward += self.longer_from_apple_punishment

        # If snake has not hit itself or walls
        if not self.snake.dead:
            # Checking whether snake has found apple
            if self.snake.found_apple(apple=self.apple):
                self._update_score()
                self.break_out_counter = 0
        else:
            self.current_reward += self.death_punishment
            self.running = False
        # Getting state resulting from given action
        new_state = self.get_state()
        # Checking that snake hasn't just started looping around
        if self.break_out_counter == self.max_iterations:
            self.running = False
            self.max_iteration_token = 1
        # Iterating counter that checks for looping snake
        else:
            self.break_out_counter += 1
        game_over = not self.running
        return self.current_reward, game_over, new_state
