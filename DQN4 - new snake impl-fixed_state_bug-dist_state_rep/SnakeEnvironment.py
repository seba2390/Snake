from Util import *
from GameObjects import *
import numpy as np


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

        # Settings
        self.display_gameplay = display_gameplay
        self.graphics_speed = graphics_speed  # chose 1,2,3,4,5,6,7
        self.apple_reward = 2.0
        self.death_punishment = -2.0
        self.max_iterations = 600
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 30, 30
        self.apple_block_size = self.apple_block_width, self.apple_block_height = 30, 30
        self.screen_size = self.screen_width, self.screen_height = 600, 600
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

        self.snake = Snake(rect=self.snake_block_rect,
                           screen_size=self.screen_size[0],
                           seed=seed)
        self.apple = Apple(rect=self.apple_block_rect,
                           screen_size=self.screen_size[0],
                           seed=seed)

    # ---- PRIVATE ---- #

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

    # ---- PUBLIC ---- #

    def get_state(self):
        # Normalized wall distances
        head = self.snake.get_head()
        _wall_danger_state = [0, 0, 0, 0]
        _wall_danger_state[0] = 1 - head.top / (self.screen_height - self.snake_block_height)
        _wall_danger_state[1] = 1 - (self.screen_height - head.bottom) / (self.screen_height - self.snake_block_height)
        _wall_danger_state[2] = 1 - head.left / (self.screen_width - self.snake_block_width)
        _wall_danger_state[3] = 1 - (self.screen_width - head.right) / (self.screen_width - self.snake_block_width)

        # Normalized snake body distances
        _snake_danger_state = [0, 0, 0, 0]  # up,down,left,right
        _current_dir = self.snake.get_direction()
        for body in range(1, self.snake.snake_length):
            if _current_dir == "up":
                # Body part in same col as head
                if head.left == self.snake.get_body(body).left:
                    # Body part in front of head (upwards)
                    if head.top >= self.snake.get_body(body).bottom:
                        # Only setting the block closest
                        inverse_dist = 1 - (head.top - self.snake.get_body(body).bottom) / \
                                           (self.screen_height - 3 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[0]:
                            _snake_danger_state[0] = inverse_dist

                # Body part in same row as head
                if head.bottom == self.snake.get_body(body).bottom:
                    # Body part to the left of head
                    if head.left >= self.snake.get_body(body).right:
                        # Only setting the block closest
                        inverse_dist = 1 - (head.left - self.snake.get_body(body).right) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[2]:
                            _snake_danger_state[2] = inverse_dist

                    # Body part to the right of head
                    if head.right <= self.snake.get_body(body).left:
                        # Only setting the block closest
                        inverse_dist = 1 - (self.snake.get_body(body).left - head.right) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[3]:
                            _snake_danger_state[3] = inverse_dist

            elif _current_dir == "down":
                # Body part in same col as head
                if head.left == self.snake.get_body(body).left:
                    # Body part in front of head (downwards)
                    if head.bottom <= self.snake.get_body(body).top:
                        # Only setting the block closest
                        inverse_dist = 1 - (self.snake.get_body(body).top - head.bottom) / \
                                           (self.screen_height - 3 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[1]:
                            _snake_danger_state[1] = inverse_dist

                # Body part in same row as head
                if head.bottom == self.snake.get_body(body).bottom:
                    # Body part to the left of head
                    if head.left >= self.snake.get_body(body).right:
                        # Only setting the block closest
                        inverse_dist = 1 - (head.left - self.snake.get_body(body).right) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[2]:
                            _snake_danger_state[2] = inverse_dist

                    # Body part to the right of head (leftwards)
                    if head.right <= self.snake.get_body(body).left:
                        # Only setting the block closest
                        inverse_dist = 1 - (self.snake.get_body(body).left - head.right) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[3]:
                            _snake_danger_state[3] = inverse_dist

            elif _current_dir == "left":
                # Body part in same row as head
                if head.bottom == self.snake.get_body(body).bottom:
                    # Body part in front of head (leftwards)
                    if head.left >= self.snake.get_body(body).right:
                        # Only setting the block closest
                        inverse_dist = 1 - (head.left - self.snake.get_body(body).right) / \
                                           (self.screen_height - 3 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[2]:
                            _snake_danger_state[2] = inverse_dist

                # Body part in same col as head
                if head.left == self.snake.get_body(body).left:
                    # Body part to the right (upwards) of head
                    if head.top >= self.snake.get_body(body).bottom:
                        # Only setting the block closest
                        inverse_dist = 1 - (head.top - self.snake.get_body(body).bottom) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[0]:
                            _snake_danger_state[0] = inverse_dist

                    # Body part to the left (downwards) of head
                    if head.bottom <= self.snake.get_body(body).top:
                        # Only setting the block closest
                        inverse_dist = 1 - (self.snake.get_body(body).top - head.bottom) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[1]:
                            _snake_danger_state[1] = inverse_dist

            elif _current_dir == "right":
                # Body part in same row as head
                if head.bottom == self.snake.get_body(body).bottom:
                    # Body part in front of head (rightwards)
                    if head.right <= self.snake.get_body(body).left:
                        # Only setting the block closest
                        inverse_dist = 1 - (self.snake.get_body(body).left - head.right) / \
                                           (self.screen_height - 3 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[3]:
                            _snake_danger_state[3] = inverse_dist

                # Body part in same col as head
                if head.left == self.snake.get_body(body).left:
                    # Body part to the left of head (upwards)
                    if head.top >= self.snake.get_body(body).bottom:
                        # Only setting the block closest
                        inverse_dist = 1 - (head.top - self.snake.get_body(body).bottom) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[0]:
                            _snake_danger_state[0] = inverse_dist

                    # Body part to the right of head
                    if head.bottom <= self.snake.get_body(body).top:
                        # Only setting the block closest
                        inverse_dist = 1 - (self.snake.get_body(body).top - head.bottom) / \
                                           (self.screen_height - 2 * self.snake_block_height)
                        if inverse_dist > _snake_danger_state[1]:
                            _snake_danger_state[1] = inverse_dist

        # Normalized apple distances
        _apple_state = [0, 0, 0, 0]
        apple = self.apple.get_apple()
        if apple.bottom <= head.top:
            _apple_state[0] = 1 - (head.top - apple.bottom) / (self.screen_height - 2 * self.snake_block_height)
        if apple.top >= head.bottom:
            _apple_state[1] = 1 - (apple.top - head.bottom) / (self.screen_height - 2 * self.snake_block_height)
        if apple.right <= head.left:
            _apple_state[2] = 1 - (head.left - apple.right) / (self.screen_height - 2 * self.snake_block_height)
        if apple.left >= head.right:
            _apple_state[3] = 1 - (apple.left - head.right) / (self.screen_height - 2 * self.snake_block_height)

        # Checking current direction
        int_2_direction = {"up": 0, "down": 1, "left": 2, "right": 3}
        _direction_state = [0, 0, 0, 0]
        _direction_state[int_2_direction[self.snake.get_direction()]] = 1

        # Distance to apple
        max_dist = np.sqrt(
            (self.screen_width - self.snake_block_width) ** 2 + (self.screen_height - self.snake_block_height) ** 2)
        dist = np.sqrt((head.centerx - apple.centerx) ** 2 + (head.centery - apple.centery) ** 2)
        _normalized_apple_dist = [dist / max_dist]

        # Distance to tail
        tail = self.snake.get_tail()
        dist = np.sqrt((head.centerx - tail.centerx) ** 2 + (head.centery - tail.centery) ** 2)
        normalized_tail_dist = [1 - dist / max_dist]

        return torch.tensor(_wall_danger_state + _snake_danger_state +
                            _apple_state + _direction_state +
                            _normalized_apple_dist + normalized_tail_dist, dtype=torch.float32).reshape(1, -1)


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
        # Updating snake state
        self.snake.update(velocity=self.snake_speed)
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
        # Iterating counter that checks for looping snake
        else:
            self.break_out_counter += 1
        game_over = not self.running
        return self.current_reward, game_over, new_state
