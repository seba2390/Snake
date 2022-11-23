from util import *
from GameObjects import *
import numpy as np

class SnakeEnvironment:
    def __init__(self, seed, neural_net=None, display_gameplay: bool = True):

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

        # Settings
        self.display_gameplay = display_gameplay
        self.graphics_speed = 1  # chose 1,2,3,4,5,6,7
        self.apple_reward = 1
        self.death_punishment = -1
        self.max_iterations = 3000
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 30, 30
        self.apple_block_size = self.apple_block_width, self.apple_block_height = 30, 30
        self.screen_size = self.screen_width, self.screen_height = 690, 690
        self.snake_speed  = self.snake_block_width  # pixels pr. frame



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


        self.initialize()

        self.snake = Snake(rect=self.snake_block_rect,
                           screen_size=self.screen_size[0],
                           seed=seed)
        self.apple = Apple(rect=self.apple_block_rect,
                           screen_size=self.screen_size[0],
                           seed=seed)

    def initialize(self):
        self.running = True
        # Initializing pygame and loading in graphics for background
        if self.display_gameplay:
            pygame.init()
            pygame.font.init()
            self.display_surf = pygame.display.set_mode(size=self.screen_size,
                                                        flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
            self.background_surf = pygame.image.load("media/background_2.png").convert()
            # Loading in graphics for snake
            self.snake_block_surf = pygame.image.load("media/snake_block_2.png").convert_alpha()
            self.snake_block_rect = self.snake_block_surf.get_rect()
            # Loading in graphics for apple
            self.apple_block_surf = pygame.image.load("media/apple_2.png").convert_alpha()
            self.apple_block_rect = self.snake_block_surf.get_rect()
            # loading in graphics for text objects
            self.score_text = PygameText(filename="media/my_font.ttf", text="score: ", text_size=25)
            self.score_text.set_position(left=30,top=5)
            self.score_value_text = PygameText(filename="media/my_font.ttf", text=str(self.current_score), text_size=25)
            self.score_value_text.set_position(left=self.score_text.rect.right + 20,top=5)
        # Using fake rects instead of graphics
        else:
            self.snake_block_rect = FakeRect(width=self.snake_block_width, height=self.snake_block_height)
            self.apple_block_rect = FakeRect(width=self.apple_block_width, height=self.apple_block_height)

    def _update_direction(self, direction: int = 42, event = None) -> None:
        # Checking for closed window
        if event.type == pygame.QUIT:
            self.running = False
            return None
        else:
             # If no neural net is given - user control is enabled
            if self.neural_net is None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT  and self.snake.get_direction() != "left":
                            self.snake.set_direction("right")
                    elif event.key == pygame.K_LEFT and self.snake.get_direction() != "right":
                            self.snake.set_direction("left")
                    elif event.key == pygame.K_UP   and self.snake.get_direction() != "down":
                            self.snake.set_direction("up")
                    elif event.key == pygame.K_DOWN and self.snake.get_direction() != "up":
                            self.snake.set_direction("down")
            # If neural net is given - directions is given by neural net
            else:
                int_2_str = {0: "right", 1: "left", 2: "up", 3: "down"}
                direction = int_2_str[direction]
                if direction == "right"  and self.snake.get_direction() != "left":
                        self.snake.set_direction("right")
                elif direction == "left" and self.snake.get_direction() != "right":
                        self.snake.set_direction("left")
                elif direction == "up"   and self.snake.get_direction() != "down":
                        self.snake.set_direction("up")
                elif direction == "down" and self.snake.get_direction() != "up":
                        self.snake.set_direction("down")

    def _update_score(self):
        self.current_score += 1
        self.loss += self.apple_reward
        self.current_reward += self.apple_reward
        if self.display_gameplay:
            current_x, current_y = self.score_value_text.rect.centerx, self.score_value_text.rect.centery
            self.score_value_text.surface = self.score_value_text.font.render(str(self.current_score), True, self.score_value_text.color, None)
            self.score_value_text.rect = self.score_value_text.surface.get_rect()
            self.score_value_text.rect.centerx, self.score_value_text.rect.centery = current_x, current_y


    def _in_game_render(self):
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
                # Checking that snake hasn't just started looping around
                if self.break_out_counter == self.max_iterations:
                    self.running = False
                    break
                # Checking whether snake has found apple
                if self.snake.found_apple(apple=self.apple):
                    self._update_score()
                    self.break_out_counter = 0
                # Iterating counter that checks for looping snake
                self.break_out_counter += 1
            else:
                self.running = False
                break
        self._close_window()
