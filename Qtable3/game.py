import matplotlib.pyplot as plt
import torch
import pygame
from pygame import *
import pygame
from pygame.locals import *
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from util import *


class SimpleSnakeApp:
    def __init__(self, seed, Q_table, display_gameplay: bool = True):

        self.seed = seed
        np.random.seed(seed=self.seed)
        self.display_gameplay = display_gameplay

        self.Q_table = Q_table
        self.current_reward = 0
        self.loss = 0

        self.apple_reward = 1
        self.snake_2_snake_punishment = -1
        self.snake_2_wall_punishment = -1

        self.max_iterations = 300
        self.break_out_counter = 0

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

        self.snake_velocity = self.snake_block_width  # pixels pr. frame
        self.snake_head_direction = np.random.choice(["up", "down", "left", "right"])
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
        self.on_init()

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
            x_fraction = self.screen_width // self.snake_block_width
            y_fraction = self.screen_height // self.snake_block_height
            x_rand = self.snake_block_width // 2 + np.random.randint(low=0, high=x_fraction) * self.snake_block_width
            y_rand = self.snake_block_height // 2 + np.random.randint(low=0, high=y_fraction) * self.snake_block_height
            assert self.snake_block_width // 2 <= x_rand <= self.screen_width - self.snake_block_width // 2
            assert self.snake_block_height // 2 <= y_rand <= self.screen_height - self.snake_block_height // 2
            self.snake_block_reacts[self.current_snake_blocks - 1].centerx = x_rand
            self.snake_block_reacts[self.current_snake_blocks - 1].centery = y_rand


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
        self.current_reward += 2*self.apple_reward
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

    def on_event(self, _event):
        if self.display_gameplay:
            if _event.type == pygame.QUIT:
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
            self.current_reward += self.snake_2_wall_punishment
            self.loss += self.snake_2_wall_punishment
            self.game_over = True
        elif snake_head.bottom > y_max or snake_head.top < y_min:
            self.current_reward += self.snake_2_wall_punishment
            self.loss += self.snake_2_wall_punishment
            self.game_over = True

    def snake_2_snake_collision_detection(self):
        if self.current_snake_blocks > 1:
            snake_head = self.snake_block_reacts[0]
            for snake_body_index in range(2, self.current_snake_blocks):
                snake_body = self.snake_block_reacts[snake_body_index]
                if self.display_gameplay:
                    if pygame.Rect.colliderect(snake_head, snake_body):
                        print("NÅR SLANGEN RAMMER SLANGEN HEHE")
                        self.current_reward += self.snake_2_snake_punishment
                        self.loss += self.snake_2_snake_punishment
                        self.game_over = True
                else:
                    if FakeColliderect(snake_head, snake_body):
                        self.current_reward += self.snake_2_snake_punishment
                        self.loss += self.snake_2_snake_punishment
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
            self.display_surf.blit(self.record_value_surface, self.record_value_react)

            self.fps.tick(40)
            pygame.display.flip()  # This is needed for image to show up ??

    def update_Q_table(self,new_qtable):
        self.Q_table = new_qtable

    def get_state(self):

        _state = [0, 0, 0, 0]

        # Snake colliding with walls
        if self.snake_block_reacts[0].top <= self.snake_block_height:  # Danger up
            _state[0] = 1
        if self.snake_block_reacts[0].bottom >= self.screen_height - self.snake_block_height:  # Danger down
            _state[0] = 2
        if self.snake_block_reacts[0].left <= self.snake_block_width:  # Danger left
            _state[0] = 3
        if self.snake_block_reacts[0].right >= self.screen_width - self.snake_block_width:  # Danger right
            _state[0] = 4

        if self.snake_head_direction == "up":  # Moving up
            _state[1] = 1
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].top <= self.snake_block_reacts[snake_body_react].bottom:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 1
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 1

        if self.snake_head_direction == "down":  # Moving down
            _state[1] = 2
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].bottom >= self.snake_block_reacts[snake_body_react].top:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 2
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 2

        if self.snake_head_direction == "left":  # Moving left
            _state[1] = 3
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].left <= self.snake_block_reacts[snake_body_react].right:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 3
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 3

        if self.snake_head_direction == "right":  # Moving right
            _state[1] = 4
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].right >= self.snake_block_reacts[snake_body_react].left:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 4
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _state[2] = 4

        if self.apple_block_react.centery < self.snake_block_reacts[0].centery:  # Apple is up from current position
            _state[3] = 1
        if self.apple_block_react.centery > self.snake_block_reacts[0].centery:  # Apple is down from current position
            _state[3] = 2
        if self.apple_block_react.centerx < self.snake_block_reacts[0].centerx:  # Apple is left from current position
            _state[3] = 3
        if self.apple_block_react.centerx > self.snake_block_reacts[0].centerx:  # Apple is right from current position
            _state[3] = 4

        return torch.tensor(_state, dtype=torch.float32)

    def get_action(self, state: torch.Tensor) -> str:
        string_representation = tensor_2_string(state)
        prediction = np.argmax(self.Q_table[string_representation]).item()
        direction_map = {0: "up", 1: "down", 2: "left", 3: "right"}
        action = direction_map[prediction]
        return action

    @staticmethod
    def get_random_action() -> str:
        direction_map = {0: "up", 1: "down", 2: "left", 3: "right"}
        index = np.random.choice(list(direction_map.keys()))
        return direction_map[index]

    def on_cleanup(self):
        if self.display_gameplay:
            pygame.quit()

    def step(self, random_flag):
        self.current_reward = 0
        current_action = None
        current_state = None
        if not self.game_over:
            if self.break_out_counter == self.max_iterations:  # If snakes starts looping around
                self.game_over = True

            current_state = self.get_state()
            if random_flag:
                current_action = self.get_random_action()
            else:
                current_action = self.get_action(current_state)
            self.control_input(current_action)

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
                self.break_out_counter = 0

            self.break_out_counter += 1

        else:
            self.running = False
        self.running = not self.game_over
        new_state = self.get_state()
        return self.current_reward, self.running, current_action, current_state, new_state

    def on_execute(self):

        if self.on_init() is False:
            self.running = False

        self.spawn_apple()
        while self.running:
            if self.display_gameplay:
                for _event in pygame.event.get():
                    self.on_event(_event)

            if not self.game_over:
                if self.break_out_counter == self.max_iterations:  # If snakes starts looping around
                    self.game_over = True

                current_state = self.get_state()
                current_action = self.get_action(current_state)

                self.control_input(current_action)

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
                    self.break_out_counter = 0

                if self.display_gameplay:
                    self.in_game_render()
                self.break_out_counter += 1
            else:
                self.running = False

        self.on_cleanup()


