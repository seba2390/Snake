import pygame
from util import *


class SimpleSnakeApp:
    def __init__(self, seed, neural_net=None, display_gameplay: bool = True):

        self.seed = seed
        np.random.seed(seed=self.seed)
        self.display_gameplay = display_gameplay
        self.graphics_speed = 4  # chose 1,2,3,4,5,6,7

        self.neural_net = None
        if neural_net is not None:
            self.neural_net = neural_net

        self.current_reward = 0
        self.loss = 0

        self.apple_reward = 1
        self.snake_2_snake_punishment = -1
        self.snake_2_wall_punishment = -1

        self.max_iterations = 3000
        self.break_out_counter = 0

        if self.display_gameplay:
            self.running = True
            self.display_surf = None
            self.background_surf = None
            self.fps = pygame.time.Clock()
        self.screen_size = self.screen_width, self.screen_height = 690, 690

        self.snake_block_surf = None
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 30, 30
        self.max_nr_snake_blocks = (self.screen_width // self.snake_block_width) * (
                self.screen_height // self.snake_block_height)
        self.snake_block_reacts = np.zeros(shape=(self.max_nr_snake_blocks,), dtype=object)
        self.current_snake_blocks = 1

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
        grid_size = self.screen_width / self.snake_block_width
        overlapping_snake = True
        while overlapping_snake:
            self.apple_block_react.left = np.random.randint(low=0, high=grid_size, size=1)[0]
            self.apple_block_react.top = np.random.randint(low=0, high=grid_size, size=1)[0]
            self.apple_block_react.left *= self.apple_block_width
            self.apple_block_react.top *= self.apple_block_height

            for snake_block in range(self.current_snake_blocks):
                if self.apple_block_react.left == self.snake_block_reacts[snake_block].left:
                    if self.apple_block_react.top == self.snake_block_reacts[snake_block].top:
                        overlapping_snake = True
                    else:
                        overlapping_snake = False
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

    def update_score(self):
        self.current_score += 1
        self.loss += self.apple_reward
        self.current_reward += self.apple_reward
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
        if event.type == pygame.QUIT:
            self.running = False

        # If no neural net is given - user control is enabled
        if self.neural_net is None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if self.snake_head_direction != "left":
                        self.snake_head_direction = "right"
                elif event.key == pygame.K_LEFT:
                    if self.snake_head_direction != "right":
                        self.snake_head_direction = "left"
                elif event.key == pygame.K_UP:
                    if self.snake_head_direction != "down":
                        self.snake_head_direction = "up"
                elif event.key == pygame.K_DOWN:
                    if self.snake_head_direction != "up":
                        self.snake_head_direction = "down"

    def control_input(self, direction: int) -> None:
        int_2_str = {0: "right", 1: "left", 2: "up", 3: "down"}
        direction = int_2_str[direction]
        assert type(direction) is str, f'action not given as str, but as {type(direction)}'
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
            #print("slange 2 væg")
            self.current_reward += self.snake_2_wall_punishment
            self.loss += self.snake_2_wall_punishment
            self.game_over = True
        elif snake_head.bottom > y_max or snake_head.top < y_min:
            #print("slange 2 væg")
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
                        #print("slange 2 slange")
                        self.current_reward += self.snake_2_snake_punishment
                        self.loss += self.snake_2_snake_punishment
                        self.game_over = True
                        break
                else:
                    if FakeColliderect(snake_head, snake_body):
                        #print("slange 2 slange")
                        self.current_reward += self.snake_2_snake_punishment
                        self.loss += self.snake_2_snake_punishment
                        self.game_over = True
                        break

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

            self.fps.tick(self.graphics_speed * 10)
            pygame.display.flip()  # This is needed for image to show up ??

    def get_state(self):

        _obstacle_state = [0, 0, 0, 0]
        # Snake colliding with walls
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
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].top <= self.snake_block_reacts[snake_body_react].bottom:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0],
                                                   self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[0] = 1
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[0] = 1

        if self.snake_head_direction == "down":  # Moving down
            _own_state[1] = 1
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].bottom >= self.snake_block_reacts[snake_body_react].top:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0],
                                                   self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[0] = 1
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[1] = 1

        if self.snake_head_direction == "left":  # Moving left
            _own_state[2] = 1
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].left <= self.snake_block_reacts[snake_body_react].right:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0],
                                                   self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[0] = 1
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[2] = 1

        if self.snake_head_direction == "right":  # Moving right
            _own_state[3] = 1
            # Snake colliding with itself
            for snake_body_react in range(1, self.current_snake_blocks):
                if self.snake_block_reacts[0].right >= self.snake_block_reacts[snake_body_react].left:
                    if self.display_gameplay:
                        if pygame.Rect.colliderect(self.snake_block_reacts[0],
                                                   self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[0] = 1
                    else:
                        if FakeColliderect(self.snake_block_reacts[0], self.snake_block_reacts[snake_body_react]):
                            _obstacle_state[3] = 1

        _apple_state = [0, 0, 0, 0]
        if self.apple_block_react.centery < self.snake_block_reacts[0].centery:  # Apple is up from current position
            _apple_state[0] = 1
        if self.apple_block_react.centery > self.snake_block_reacts[0].centery:  # Apple is down from current position
            _apple_state[1] = 1
        if self.apple_block_react.centerx < self.snake_block_reacts[0].centerx:  # Apple is left from current position
            _apple_state[2] = 1
        if self.apple_block_react.centerx > self.snake_block_reacts[0].centerx:  # Apple is right from current position
            _apple_state[3] = 1
        return torch.tensor(_obstacle_state + _own_state + _apple_state, dtype=torch.float32).reshape(1, -1)

    def get_state_2(self):

        _wall_danger_state = [0, 0, 0, 0]
        # Checking for danger UP (if wall is within 1 block)
        if self.snake_block_reacts[0].top <= self.snake_block_height:
            _wall_danger_state[0] = 1
        # Checking for danger DOWN (if wall is within 1 block)
        if self.snake_block_reacts[0].bottom >= self.screen_height - self.snake_block_height:
            _wall_danger_state[1] = 1
        # Checking for danger LEFT (if wall is within 1 block)
        if self.snake_block_reacts[0].left <= self.snake_block_width:
            _wall_danger_state[2] = 1
        # Checking for danger RIGHT (if wall is within 1 block)
        if self.snake_block_reacts[0].left >= self.screen_width - self.snake_block_width:
            _wall_danger_state[3] = 1

        _snake_danger_state = [0, 0, 0, 0]
        # Checking for danger UP (if snake body is within 1 block)
        for snake_block in range(1, self.current_snake_blocks):
            # Should be at same col in grid
            if self.snake_block_reacts[snake_block].centerx == self.snake_block_reacts[0].centerx:
                y1, y2 = self.snake_block_reacts[snake_block].top, self.snake_block_reacts[0].top
                if y1 <= y2:
                    if np.abs(y1 - y2) <= 2 * self.snake_block_height:
                        _snake_danger_state[0] = 1
        # Checking for danger DOWN (if snake body is within 1 block)
        for snake_block in range(1, self.current_snake_blocks):
            # Should be at same col in grid
            if self.snake_block_reacts[snake_block].centerx == self.snake_block_reacts[0].centerx:
                y1, y2 = self.snake_block_reacts[snake_block].bottom, self.snake_block_reacts[0].bottom
                if y1 >= y2:
                    if np.abs(y1 - y2) <= 2 * self.snake_block_height:
                        _snake_danger_state[1] = 1
        # Checking for danger LEFT (if snake body is within 1 block)
        for snake_block in range(1, self.current_snake_blocks):
            # Should be at same row in grid
            if self.snake_block_reacts[snake_block].centery == self.snake_block_reacts[0].centery:
                x1, x2 = self.snake_block_reacts[snake_block].bottom, self.snake_block_reacts[0].bottom
                if x1 <= x2:
                    if np.abs(x1 - x2) <= 2 * self.snake_block_width:
                        _snake_danger_state[2] = 1
        # Checking for danger RIGHT (if snake body is within 1 block)
        for snake_block in range(1, self.current_snake_blocks):
            # Should be at same row in grid
            if self.snake_block_reacts[snake_block].centery == self.snake_block_reacts[0].centery:
                x1, x2 = self.snake_block_reacts[snake_block].bottom, self.snake_block_reacts[0].bottom
                if x1 >= x2:
                    if np.abs(x1 - x2) <= 2 * self.snake_block_width:
                        _snake_danger_state[3] = 1

        _direction_state = [0, 0, 0, 0]
        str_2_int = {"right": 0, "left": 1, "up": 2, "down": 3}
        _direction_state[str_2_int[self.snake_head_direction]] = 1

        _apple_state = [0, 0, 0, 0]
        if self.apple_block_react.centery < self.snake_block_reacts[0].centery:  # Apple is up from current position
            _apple_state[0] = 1
        if self.apple_block_react.centery > self.snake_block_reacts[0].centery:  # Apple is down from current position
            _apple_state[1] = 1
        if self.apple_block_react.centerx < self.snake_block_reacts[0].centerx:  # Apple is left from current position
            _apple_state[2] = 1
        if self.apple_block_react.centerx > self.snake_block_reacts[0].centerx:  # Apple is right from current position
            _apple_state[3] = 1
        return torch.tensor(_wall_danger_state + _snake_danger_state + _direction_state + _apple_state, dtype=torch.float32).reshape(1, -1)

    def on_cleanup(self):
        if self.display_gameplay:
            pygame.quit()

    def step(self, action):
        self.current_reward = 0
        new_state = None
        if not self.game_over:
            if self.break_out_counter == self.max_iterations:  # If snakes starts looping around
                self.game_over = True

            self.control_input(action)

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

            # Weird bug - sometimes apple spawns inside snake even though it shouldn't - this should fix it
            if self.apple_in_snake():
                while self.apple_in_snake():
                    self.spawn_apple()
            assert self.apple_in_snake() is False

            new_state = self.get_state_2()

            self.break_out_counter += 1
        if self.current_reward < self.snake_2_snake_punishment:
            print("whaaaaaaaaat")
        return self.current_reward, self.game_over, new_state

    def apple_in_snake(self):
        result = False
        for snake_block in range(self.current_snake_blocks):
            if self.apple_block_react.left == self.snake_block_reacts[snake_block].left:
                if self.apple_block_react.top == self.snake_block_reacts[snake_block].top:
                    result = True
        for snake_block in range(self.current_snake_blocks):
            if self.display_gameplay:
                if pygame.Rect.colliderect(self.apple_block_react, self.snake_block_reacts[snake_block]):
                    result = True
            else:
                if FakeColliderect(self.apple_block_react, self.snake_block_reacts[snake_block]):
                    result = True
        return result

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
                    break

                if self.neural_net is not None:
                    current_state = self.get_state_2()
                    possible_actions = self.neural_net.forward(current_state)
                    current_action_index = torch.argmax(input=self.neural_net.forward(current_state)).item()
                    self.control_input(current_action_index)

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

                # Weird bug - sometimes apple spawns inside snake even though it shouldn't - this should fix it
                if self.apple_in_snake():
                    while self.apple_in_snake():
                        self.spawn_apple()
                assert self.apple_in_snake() is False

                if self.display_gameplay:
                    self.in_game_render()

                self.break_out_counter += 1
            else:
                self.running = False

        self.on_cleanup()
