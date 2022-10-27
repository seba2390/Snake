import matplotlib.pyplot as plt
import torch
from NeuralNet import *
import pygame
from pygame import *
import pygame
from pygame.locals import *
import numpy as np
from copy import deepcopy
from tqdm import tqdm


class FakeReact:
    """ Imitation type class implementation of Pygame Reacts.
        Needs 'width' and 'height' for initialization, but auto-adjusts,
        remaining params when one is adjusted and implements
        'property' type setter/getter attributes."""

    def __init__(self, height, width,
                 centerx: int = 0,
                 centery: int = 0,
                 left: int = 0,
                 right: int = 0,
                 top: int = 0,
                 bottom: int = 0):
        self._height = height
        self._width = width
        self._centerx = centerx
        self._centery = centery
        self._left = left
        self._right = right
        self._top = top
        self._bottom = bottom

    def _get_right(self):
        return self._right

    def _set_right(self, value):
        self._right = value
        self._left = self._right - self._width
        self._centerx = self._right - self._width // 2

    def _del_right(self):
        del self._right

    right = property(
        fget=_get_right,
        fset=_set_right,
        fdel=_del_right,
        doc="The right property."
    )

    def _get_left(self):
        return self._left

    def _set_left(self, value):
        self._left = value
        self._right = self._left + self._width
        self._centerx = self._left + self._width // 2

    def _del_left(self):
        del self._left

    left = property(
        fget=_get_left,
        fset=_set_left,
        fdel=_del_left,
        doc="The left property."
    )

    def _get_centerx(self):
        return self._centerx

    def _set_centerx(self, value):
        self._centerx = value
        self._left = self._centerx - self._width // 2
        self._right = self._left + self._width

    def _del_centerx(self):
        del self._centerx

    centerx = property(
        fget=_get_centerx,
        fset=_set_centerx,
        fdel=_del_centerx,
        doc="The centerx property."
    )

    def _get_centery(self):
        return self._centery

    def _set_centery(self, value):
        self._centery = value
        self._top = self._centery - self._height // 2
        self._bottom = self._top + self._height

    def _del_centery(self):
        del self._centery

    centery = property(
        fget=_get_centery,
        fset=_set_centery,
        fdel=_del_centery,
        doc="The centery property."
    )

    def _get_top(self):
        return self._top

    def _set_top(self, value):
        self._top = value
        self._centery = self._top + self._height // 2
        self._bottom = self._top + self._height

    def _del_top(self):
        del self._top

    top = property(
        fget=_get_top,
        fset=_set_top,
        fdel=_del_top,
        doc="The top property."
    )

    def _get_bottom(self):
        return self._bottom

    def _set_bottom(self, value):
        self._bottom = value
        self._centery = self._bottom - self._height // 2
        self._top = self._bottom - self._height

    def _del_bottom(self):
        del self._bottom

    bottom = property(
        fget=_get_bottom,
        fset=_set_bottom,
        fdel=_del_bottom,
        doc="The bottom property."
    )

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def move(self, x, y):
        self._set_centerx(self._centerx + x)
        self._set_centery(self._centery + y)
        return FakeReact(width=self._width,
                         height=self._height,
                         centerx=self._centerx,
                         centery=self._centery,
                         left=self._left,
                         right=self._right,
                         top=self._top,
                         bottom=self._bottom)


def FakeColliderect(fakerect1: FakeReact,
                    fakerect2: FakeReact) -> bool:
    if fakerect2.left <= fakerect1.left <= fakerect2.right:
        if fakerect2.top <= fakerect1.top <= fakerect2.bottom:
            return True
        elif fakerect1.top <= fakerect2.top <= fakerect1.bottom:
            return True
        return False
    elif fakerect1.left <= fakerect2.left <= fakerect1.right:
        if fakerect2.top <= fakerect1.top <= fakerect2.bottom:
            return True
        elif fakerect1.top <= fakerect2.top <= fakerect1.bottom:
            return True
        return False
    return False


class SimpleSnakeApp:
    def __init__(self, neural_net, display_gameplay: bool = True):

        self.display_gameplay = display_gameplay

        if self.display_gameplay:
            self.running = True
            self.display_surf = None
            self.background_surf = None
            self.fps = pygame.time.Clock()
        self.screen_size = self.screen_width, self.screen_height = 690, 690

        self.snake_block_surf = None
        self.max_nr_snake_blocks = 400
        self.snake_block_reacts = np.zeros(shape=(self.max_nr_snake_blocks,), dtype=object)
        self.current_snake_blocks = 1
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 30, 30
        self.max_nr_snake_blocks = (self.screen_width / self.snake_block_width) * (
                self.screen_height / self.snake_block_height)

        self.snake_velocity = 30  # pixels pr. frame
        self.snake_head_direction = "up"
        self.snake_head_history = []
        self.spawn_delay = int(self.snake_block_height / self.snake_velocity)
        self.spawn_snake_block_flag = False

        self.apple_block_surf = None
        self.apple_block_react = None
        self.apple_block_size = self.apple_block_width, self.apple_block_height = 30, 30
        self.spawn_apple_flag = True
        self.game_over = False
        self.current_score = 0

        if self.display_gameplay:
            pygame.font.init()
            self.text_color = (255, 255, 255)  # White
            self.score_board_font = pygame.font.Font("media/my_font.ttf", 25)
            self.score_text_surface = self.score_board_font.render("score: ", True, self.text_color, None)
            self.score_text_react = self.score_text_surface.get_rect()
            self.score_text_react.left = 30
            self.score_text_react.top = 5

            self.score_value_surface = self.score_board_font.render(str(self.current_score), True, self.text_color,
                                                                    None)
            self.score_value_react = self.score_value_surface.get_rect()
            self.score_value_react.left = self.score_text_react.right + 20
            self.score_value_react.top = 5

            self.deaths_text_surface = self.score_board_font.render("deaths: ", True, self.text_color, None)
            self.deaths_text_react = self.deaths_text_surface.get_rect()
            self.deaths_text_react.left = self.screen_width // 2 - 55
            self.deaths_text_react.top = 5

            self.nr_deaths = 0
            self.deaths_value_surface = self.score_board_font.render(str(self.nr_deaths), True, self.text_color, None)
            self.deaths_value_react = self.deaths_value_surface.get_rect()
            self.deaths_value_react.left = self.screen_width // 2 + 30
            self.deaths_value_react.top = 5

            self.record_text_surface = self.score_board_font.render("record: ", True, self.text_color, None)
            self.record_text_react = self.record_text_surface.get_rect()
            self.record_text_react.left = self.screen_width - 120
            self.record_text_react.top = 5

            self.record = 0
            self.record_value_surface = self.score_board_font.render(str(self.nr_deaths), True, self.text_color, None)
            self.record_value_react = self.record_value_surface.get_rect()
            self.record_value_react.left = self.screen_width - 45
            self.record_value_react.top = 5

        self.ratio = self.screen_width / self.snake_block_width - 1
        self.apple_distances = []
        self.max_iterations = 1000
        self.break_out_counter = 0
        self.game_over_punishment = 20
        self.apple_reward = -20
        self.step_closer_reward = (self.apple_reward / 10) / self.max_iterations
        assert self.step_closer_reward < 0
        self.step_away_punishment = -(self.apple_reward / 10) / self.max_iterations
        assert self.step_away_punishment > 0
        self.loss = 0
        self.neural_net = neural_net

    def on_init(self):
        # Initializing pygame and loading in graphics for background
        self.running = True
        if self.display_gameplay:
            pygame.init()

            self.display_surf = pygame.display.set_mode(size=self.screen_size,
                                                        flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        if self.display_gameplay:
            self.background_surf = pygame.image.load("media/background_2.png").convert()

        # Loading in graphics for snake
        if self.display_gameplay:
            self.snake_block_surf = pygame.image.load("media/snake_block_2.png").convert_alpha()
            self.snake_block_reacts[self.current_snake_blocks - 1] = self.snake_block_surf.get_rect()

            self.snake_block_reacts[self.current_snake_blocks - 1].left = 10 * self.snake_block_width
            self.snake_block_reacts[self.current_snake_blocks - 1].top = 10 * self.snake_block_height
        else:
            self.snake_block_reacts[self.current_snake_blocks - 1] = FakeReact(width=self.snake_block_width,
                                                                               height=self.snake_block_height)
            self.snake_block_reacts[self.current_snake_blocks - 1].left = 10 * self.snake_block_width
            self.snake_block_reacts[self.current_snake_blocks - 1].top = 10 * self.snake_block_height

        # Loading in graphics for apple¨
        if self.display_gameplay:
            self.apple_block_surf = pygame.image.load("media/apple_2.png").convert_alpha()
            self.apple_block_react = self.snake_block_surf.get_rect()
        else:
            self.apple_block_react = FakeReact(width=self.apple_block_width,
                                               height=self.apple_block_height)

    def spawn_snake_block(self):
        self.spawn_snake_block_flag = False
        if self.display_gameplay:
            snake_block = self.snake_block_surf.get_rect()
        else:
            snake_block = FakeReact(width=self.snake_block_width,
                                    height=self.snake_block_height)
        index = self.current_snake_blocks - 1
        if self.snake_head_history[0][2] == 'right':
            snake_block.centerx = self.snake_block_reacts[index].centerx - self.snake_block_width
            snake_block.centery = self.snake_block_reacts[index].centery
        elif self.snake_head_history[0][2] == 'left':
            snake_block.centerx = self.snake_block_reacts[index].centerx + self.snake_block_width
            snake_block.centery = self.snake_block_reacts[index].centery
        elif self.snake_head_history[0][2] == 'up':
            snake_block.centerx = self.snake_block_reacts[index].centerx
            snake_block.centery = self.snake_block_reacts[index].centery + self.snake_block_height
        elif self.snake_head_history[0][2] == 'down':
            snake_block.centerx = self.snake_block_reacts[index].centerx
            snake_block.centery = self.snake_block_reacts[index].centery - self.snake_block_height
        self.snake_block_reacts[self.current_snake_blocks] = snake_block
        self.current_snake_blocks += 1

    def spawn_apple(self):
        self.spawn_apple_flag = False
        x_max = self.screen_width - self.apple_block_width
        y_max = self.screen_width - self.apple_block_height
        overlapping_snake = True
        while overlapping_snake:
            self.apple_block_react.left = np.random.randint(low=0, high=self.ratio, size=1)[0]
            self.apple_block_react.top = np.random.randint(low=0, high=self.ratio, size=1)[0]
            self.apple_block_react.left *= self.apple_block_width
            self.apple_block_react.top *= self.apple_block_height
            for snake_block in range(self.current_snake_blocks):
                if self.display_gameplay:
                    if pygame.Rect.colliderect(self.apple_block_react, self.snake_block_reacts[snake_block]):
                        overlapping_snake = True
                    else:
                        overlapping_snake = False
                else:
                    if FakeColliderect(self.apple_block_react, self.snake_block_reacts[snake_block]):
                        overlapping_snake = True
                    else:
                        overlapping_snake = False

    def initial_spawn_apple(self):
        self.spawn_apple_flag = False
        x_max = self.screen_width - self.apple_block_width
        y_max = self.screen_width - self.apple_block_height
        self.apple_block_react.left = 3 * self.apple_block_width
        self.apple_block_react.top = 3 * self.apple_block_height

    def update_score(self):
        self.current_score += 1
        self.loss += 2*self.apple_reward
        if self.display_gameplay:
            current_x, current_y = self.score_value_react.centerx, self.score_value_react.centery
            self.score_value_surface = self.score_board_font.render(str(self.current_score), True, self.text_color,
                                                                    None)
            self.score_value_react = self.score_value_surface.get_rect()
            self.score_value_react.centerx, self.score_value_react.centery = current_x, current_y

    def update_snake_head_position(self):
        if self.snake_head_direction == "right":
            self.snake_block_reacts[0] = self.snake_block_reacts[0].move(self.snake_velocity, 0)
        elif self.snake_head_direction == "left":
            self.snake_block_reacts[0] = self.snake_block_reacts[0].move(-self.snake_velocity, 0)
        elif self.snake_head_direction == "up":
            self.snake_block_reacts[0] = self.snake_block_reacts[0].move(0, -self.snake_velocity)
        elif self.snake_head_direction == "down":
            self.snake_block_reacts[0] = self.snake_block_reacts[0].move(0, self.snake_velocity)

    def update_snake_body_position(self):
        if self.current_snake_blocks > 1:
            for snake_body_block in range(1, self.current_snake_blocks):
                history_index = snake_body_block * self.spawn_delay
                history_len = len(self.snake_head_history) - 1
                self.snake_block_reacts[snake_body_block].centerx = \
                    self.snake_head_history[history_len - history_index][0]
                self.snake_block_reacts[snake_body_block].centery = \
                    self.snake_head_history[history_len - history_index][1]

    def save_snake_head_history(self):
        self.snake_head_history.append([self.snake_block_reacts[0].centerx,
                                        self.snake_block_reacts[0].centery,
                                        self.snake_head_direction])

    def update_snake_head_history(self):
        history_length = self.current_snake_blocks * self.spawn_delay
        if len(self.snake_head_history) > history_length:
            self.snake_head_history = self.snake_head_history[(len(self.snake_head_history) - history_length):]

    def on_event(self, event):
        if self.display_gameplay:
            if event.type == pygame.QUIT:
                self.running = False

    def control_input(self, direction):
        if direction == "right":
            if self.snake_head_direction != "left":
                self.snake_head_direction = "right"
        elif direction == "left":
            if self.snake_head_direction != "right":
                self.snake_head_direction = "left"
        elif direction == "up":
            if self.snake_head_direction != "down":
                self.snake_head_direction = "up"
        elif direction == "down":
            if self.snake_head_direction != "up":
                self.snake_head_direction = "down"

    def control_input_2(self, direction):

        # Perform right turn
        if direction == "right":
            if self.snake_head_direction == "left":
                self.snake_head_direction = "up"
            elif self.snake_head_direction == "up":
                self.snake_head_direction = "right"
            elif self.snake_head_direction == "right":
                self.snake_head_direction = "down"
            elif self.snake_head_direction == "down":
                self.snake_head_direction = "left"

        # Perform left turn
        elif direction == "left":
            if self.snake_head_direction == "right":
                self.snake_head_direction = "up"
            elif self.snake_head_direction == "down":
                self.snake_head_direction = "right"
            elif self.snake_head_direction == "left":
                self.snake_head_direction = "down"
            elif self.snake_head_direction == "up":
                self.snake_head_direction = "left"

        # Continue in same direction
        elif direction == "up":
            self.snake_head_direction = self.snake_head_direction

    def snake_2_apple_collision_detection(self):
        if self.display_gameplay:
            if pygame.Rect.colliderect(self.apple_block_react, self.snake_block_reacts[0]):
                self.spawn_apple_flag = True
                self.spawn_snake_block_flag = True
                self.update_score()
        else:
            if FakeColliderect(self.apple_block_react, self.snake_block_reacts[0]):
                self.spawn_apple_flag = True
                self.spawn_snake_block_flag = True
                self.update_score()

    def snake_2_wall_collision_detection(self):
        x_min, x_max = 0, self.screen_width
        y_min, y_max = 0, self.screen_width
        snake_head = self.snake_block_reacts[0]
        if snake_head.left < x_min or snake_head.right > x_max:
            self.game_over = True
        elif snake_head.bottom > y_max or snake_head.top < y_min:
            self.game_over = True

    def snake_2_snake_collision_detection(self):
        if self.current_snake_blocks > 1:
            snake_head = self.snake_block_reacts[0]
            for snake_body_index in range(2, self.current_snake_blocks):
                snake_body = self.snake_block_reacts[snake_body_index]
                if self.display_gameplay:
                    if pygame.Rect.colliderect(snake_head, snake_body):
                        self.game_over = True
                else:
                    if FakeColliderect(snake_head, snake_body):
                        self.game_over = True

    def in_game_render(self):
        if self.display_gameplay:
            # Rendering background
            self.display_surf.blit(self.background_surf, (0, 0))
            # Rendering snake
            for snake_block in range(self.current_snake_blocks):
                self.display_surf.blit(self.snake_block_surf, self.snake_block_reacts[snake_block])
            # Rendering apple
            self.display_surf.blit(self.apple_block_surf, self.apple_block_react)
            # Rendering score text
            self.display_surf.blit(self.score_text_surface, self.score_text_react)
            # Rendering score value
            self.display_surf.blit(self.score_value_surface, self.score_value_react)
            # Rendering nr deaths text
            self.display_surf.blit(self.deaths_text_surface, self.deaths_text_react)
            # Rendering nr deaths value
            self.display_surf.blit(self.deaths_value_surface, self.deaths_value_react)
            # Rendering record text
            self.display_surf.blit(self.record_text_surface, self.record_text_react)
            # Rendering record value
            self.display_surf.blit(self.record_value_surface, self.record_value_react
                                   )
            self.fps.tick(20)
            pygame.display.flip()  # This is needed for image to show up ??

    def get_state(self):

        _obstacle_state = [0, 0, 0, 0]
        if self.snake_block_reacts[0].top < self.snake_block_height:
            _obstacle_state[0] = 1
        if self.snake_block_reacts[0].bottom > self.screen_height - self.snake_block_height:
            _obstacle_state[1] = 1
        if self.snake_block_reacts[0].left < self.snake_block_width:
            _obstacle_state[2] = 1
        if self.snake_block_reacts[0].right > self.screen_width - self.snake_block_width:
            _obstacle_state[3] = 1

        snake_head_pos = [self.snake_block_reacts[0].centerx, self.snake_block_reacts[0].centery]
        snake_head_pos[0] *= 1.0 / (self.screen_width - self.snake_block_width / 2)
        snake_head_pos[1] *= 1.0 / (self.screen_height - self.snake_block_height / 2)

        apple_pos = [self.apple_block_react.centerx, self.apple_block_react.centery]
        apple_pos[0] *= 1.0 / (self.screen_width - self.apple_block_width / 2)
        apple_pos[1] *= 1.0 / (self.screen_height - self.apple_block_height / 2)

        return torch.tensor(_obstacle_state + snake_head_pos + apple_pos, dtype=torch.float32)

    def get_state_2(self):
        _obstacle_state = [1, 1, 1, 1]
        if self.snake_block_reacts[0].top < self.snake_block_height:
            _obstacle_state[0] = 0
        if self.snake_block_reacts[0].bottom > self.screen_height - self.snake_block_height:
            _obstacle_state[1] = 0
        if self.snake_block_reacts[0].left < self.snake_block_width:
            _obstacle_state[2] = 0
        if self.snake_block_reacts[0].right > self.screen_width - self.snake_block_width:
            _obstacle_state[3] = 0

        _apple_state = [0, 0]
        if self.apple_block_react.centerx == self.snake_block_reacts[0].centerx:
            _apple_state[0] = 1
        if self.apple_block_react.centery == self.snake_block_reacts[0].centery:
            _apple_state[1] = 1

        _max_distance = np.sqrt((self.screen_width - self.snake_block_width) ** 2 + (self.screen_height - self.snake_block_height) ** 2)
        _distance_state = [self.distance_2_apple() / _max_distance]
        return torch.tensor(_obstacle_state + _apple_state + _distance_state, dtype=torch.float32)

    def get_state_3(self):
        _obstacle_state = [0, 0, 0, 0]
        if self.snake_block_reacts[0].top <= self.snake_block_height:  # Danger up
            _obstacle_state[0] = 1
        if self.snake_block_reacts[0].bottom >= self.screen_height - self.snake_block_height:  # Danger down
            _obstacle_state[1] = 1
        if self.snake_block_reacts[0].left <= self.snake_block_width:  # Danger left
            _obstacle_state[2] = 1
        if self.snake_block_reacts[0].right >= self.screen_width - self.snake_block_width:  # Danger right
            _obstacle_state[3] = 1

        _own_state = [0, 0, 0, 0]
        if self.snake_head_direction == "up":  # Moving up
            _own_state[0] = 1
        if self.snake_head_direction == "down":  # Moving down
            _own_state[1] = 1
        if self.snake_head_direction == "left":  # Moving left
            _own_state[2] = 1
        if self.snake_head_direction == "right":  # Moving right
            _own_state[3] = 1

        _apple_state = [0, 0, 0, 0]
        if self.apple_block_react.centery < self.snake_block_reacts[0].centery: # Apple is up from current position
            _apple_state[0] = 1
        if self.apple_block_react.centery > self.snake_block_reacts[0].centery: # Apple is down from current position
            _apple_state[1] = 1
        if self.apple_block_react.centerx < self.snake_block_reacts[0].centerx: # Apple is left from current position
            _apple_state[2] = 1
        if self.apple_block_react.centerx > self.snake_block_reacts[0].centerx: # Apple is right from current position
            _apple_state[3] = 1

        return torch.tensor(_obstacle_state + _own_state + _apple_state, dtype=torch.float32)

    def distance_2_apple(self):
        return np.sqrt((self.apple_block_react.centerx - self.snake_block_reacts[0].centerx) ** 2 + (
                    self.apple_block_react.centery - self.snake_block_reacts[0].centery) ** 2)

    @staticmethod
    def output_2_direction(output):
        direction_map = {0: "up", 1: "down", 2: "left", 3: "right"}
        assert len(output) == len(list(direction_map.keys()))
        argmax = torch.argmax(output).item()
        return direction_map[argmax]

    @staticmethod
    def output_2_direction_2(output):
        direction_map = {0: "up", 1: "left", 2: "right"}
        assert len(output) == len(list(direction_map.keys()))
        argmax = torch.argmax(output).item()
        return direction_map[argmax]

    def on_cleanup(self):
        if self.display_gameplay:
            pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self.running = False

        self.spawn_apple()
        self.apple_distances.append(self.distance_2_apple())
        while self.running:
            if self.display_gameplay:
                for event in pygame.event.get():
                    self.on_event(event)

            if not self.game_over:
                if self.break_out_counter == 1000:  # If snakes starts looping around
                    self.game_over = True

                current_state = self.get_state_3()
                current_prediction = self.neural_net.forward(current_state)
                current_direction = self.output_2_direction(current_prediction)
                self.control_input(direction=current_direction)

                self.update_snake_head_position()
                self.snake_2_snake_collision_detection()
                self.snake_2_apple_collision_detection()
                self.snake_2_wall_collision_detection()

                self.save_snake_head_history()
                self.update_snake_head_history()
                self.update_snake_body_position()

                if self.spawn_snake_block_flag:
                    self.spawn_snake_block()

                if self.spawn_apple_flag:
                    self.spawn_apple()

                if not self.game_over:
                    distance_2_apple = self.distance_2_apple()
                    # Closer to apple = reward
                    if distance_2_apple < self.apple_distances[-1]:
                        self.loss += self.step_closer_reward
                    # Longer away from apple = punishment
                    else:
                        self.loss += self.step_away_punishment
                if self.display_gameplay:
                    self.in_game_render()
                self.break_out_counter += 1
            else:
                # self.loss += self.game_over_punishment
                self.running = False

        self.on_cleanup()


if __name__ == "__main__":

    loss_means = []
    highest_scores = []
    best_play_models = []

    # Initial run
    nr_agents = 10000
    agents = [NeuralNetwork() for agent in range(nr_agents)]
    losses = []
    scores = []
    for agent in tqdm(range(nr_agents)):
        theApp = SimpleSnakeApp(neural_net=agents[agent],
                                display_gameplay=False)
        theApp.on_execute()
        losses.append(theApp.loss)
        scores.append(theApp.current_score)

    iterations = [i + 1 for i in range(nr_agents)]
    plt.plot(iterations, losses)
    plt.plot(iterations, losses, 'o', ms=1)
    plt.savefig("generation_losses/" + "initial" + "_generation.pdf")
    plt.show()
    plt.cla()
    plt.clf()
    plt.close()

    print("highest score: ", np.max(scores))
    highest_scores.append(np.max(scores))
    loss_means.append(np.mean(losses))

    nr_generations = 3
    nr_replays = 3
    nr_best = 3
    lr = 0.00000001
    for generation in range(nr_generations):
        _best_agents = np.array(agents)[np.argsort(np.array(losses))][:nr_best]
        _agents = agents
        _losses = losses
        _scores = None
        for replay in tqdm(range(nr_replays)):
            # Picking out 'nr_best' agents and adding some mutation
            agents = [a for a in _best_agents]
            nr_copies = int((nr_agents / 10 - len(agents)) / len(_best_agents))
            for best_agent in _best_agents:
                for copy in range(nr_copies):
                    agents.append(best_agent)
            # Second run
            losses = []
            scores = []
            for agent in range(len(agents)):
                theApp = SimpleSnakeApp(neural_net=agents[agent],
                                        display_gameplay=False)
                theApp.on_execute()
                losses.append(theApp.loss)
                scores.append(theApp.current_score)
            _agents = agents
            _best_agents = np.array(_agents)[np.argsort(np.array(losses))][:nr_best]
            _losses = losses
            _scores = scores

        nr_mutations = int((nr_agents / 10 - nr_best) / len(_best_agents))
        for best_agent in _best_agents:
            for mutation in range(nr_mutations):
                mutated_agent = deepcopy(best_agent)
                for layer_name in mutated_agent.state_dict():
                    if "weight" not in layer_name and 'bias' not in layer_name:
                        continue
                    mutated_agent.state_dict()[layer_name] += lr * torch.normal(mean=0, std=torch.ones(size=mutated_agent.state_dict()[layer_name].shape))
                    #mutated_agent.state_dict()[layer_name] += lr*torch.rand(size=mutated_agent.state_dict()[layer_name].shape)
                agents.append(mutated_agent)

        loss_means.append(np.mean(_losses))
        best_play_models.append(np.array(_agents)[np.argmin(_losses)])
        highest_scores.append(np.max(_scores))

        print("generation: ", generation + 1)
        print("highest score: ", np.max(_scores))
        highest_scores.append(np.max(_scores))

        iterations = [i + 1 for i in range(len(_losses))]
        plt.plot(iterations, _losses)
        plt.plot(iterations, _losses, 'o', ms=1)
        plt.savefig("generation_losses/" + str(generation + 1) + "_generation.pdf")
        plt.show()
        plt.cla()
        plt.clf()
        plt.close()

    generations = [i + 1 for i in range(len(loss_means))]
    plt.plot(generations, loss_means)
    plt.plot(generations, loss_means, 'o', ms=1)
    plt.savefig("generation_losses/" + "loss_means.pdf")
    plt.xlabel("Generation")
    plt.show()

    generations = [i + 1 for i in range(len(highest_scores))]
    plt.plot(generations, highest_scores)
    plt.plot(generations, highest_scores, 'o', ms=1)
    plt.xlabel("Generation")
    plt.savefig("generation_losses/" + "highest_scores.pdf")
    plt.show()

    # playing the best agent in each of the games
    replay = True
    if replay:
        for agent in best_play_models:
            theApp = SimpleSnakeApp(neural_net=agent,
                                    display_gameplay=True)
            theApp.on_execute()
