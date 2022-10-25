import pygame
from pygame.locals import *
import numpy as np
from copy import deepcopy

# TODO: fix problem with snake head hitting two apples within 'self.spawn_delay' nr. of frames

class SnakeApp:
    def __init__(self):
        self.running = True
        self.display_surf = None
        self.background_surf = None
        self.screen_size = self.screen_width, self.screen_height = 714, 777
        self.frame_width = int((self.screen_width - 700) / 2)+2
        self.fps = pygame.time.Clock()

        self.snake_block_surf = None
        self.snake_block_reacts = []
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 35, 35

        self.snake_velocity = 5  # pixels pr. frame
        self.snake_head_direction = None
        self.snake_head_history = []
        self.spawn_delay = int(self.snake_block_height/self.snake_velocity)
        self.spawn_snake_block_flag = False

        self.apple_block_surf = None
        self.apple_block_react = None
        self.apple_block_size = self.apple_block_width, self.apple_block_height = 35, 35
        self.spawn_apple_flag = True

        pygame.font.init()
        self.text_color = (255, 255, 255)  # White
        self.score_board_font = pygame.font.Font("media/arcade_classic.ttf", 30)
        self.score_text_surface = self.score_board_font.render("score: ", True, self.text_color, None)
        self.score_text_react = self.score_text_surface.get_rect()
        self.score_text_react.left = self.frame_width + 5
        self.score_text_react.bottom = self.screen_height - self.frame_width - 5

        self.current_score = 0
        self.score_value_surface = self.score_board_font.render(str(self.current_score), True, self.text_color, None)
        self.score_value_react = self.score_value_surface.get_rect()
        self.score_value_react.left = self.score_text_react.right + 10
        self.score_value_react.bottom = self.screen_height - self.frame_width - 5

    def on_init(self):
        # Initializing pygame and loading in graphics for background
        pygame.init()
        self.running = True
        self.display_surf = pygame.display.set_mode(size=self.screen_size,
                                                    flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self.background_surf = pygame.image.load("media/background.png").convert()

        # Loading in graphics for snake
        self.snake_block_surf = pygame.image.load("media/snake_block.png").convert_alpha()
        self.snake_block_reacts.append(self.snake_block_surf.get_rect())
        self.snake_block_reacts[0].centerx = int(self.screen_width/2)
        self.snake_block_reacts[0].centery = int(self.screen_height/2)

        # Loading in graphics for apple
        self.apple_block_surf = pygame.image.load("media/apple.png").convert_alpha()
        self.apple_block_react = self.snake_block_surf.get_rect()

    def spawn_snake_block(self):
        self.spawn_snake_block_flag = False
        snake_block = self.snake_block_surf.get_rect()
        if self.snake_head_direction == 'right':
            snake_block.centerx = self.snake_block_reacts[-1].left - self.snake_block_width//2
            snake_block.centery = self.snake_block_reacts[-1].centery
        elif self.snake_head_direction == 'left':
            snake_block.centerx = self.snake_block_reacts[-1].right + self.snake_block_width//2
            snake_block.centery = self.snake_block_reacts[-1].centery
        elif self.snake_head_direction == 'up':
            snake_block.centerx = self.snake_block_reacts[-1].centerx
            snake_block.centery = self.snake_block_reacts[-1].bottom + self.snake_block_height//2
        elif self.snake_head_direction == 'down':
            snake_block.centerx = self.snake_block_reacts[-1].centerx
            snake_block.centery = self.snake_block_reacts[-1].top - self.snake_block_height//2
        self.snake_block_reacts.append(snake_block)

    def spawn_apple(self):
        if self.spawn_apple_flag:
            self.spawn_apple_flag = False
            x_min = self.frame_width + int(self.apple_block_width / 2)
            x_max = self.screen_width - self.frame_width - int(self.apple_block_width / 2)
            y_min = self.frame_width + int(self.apple_block_height / 2)
            y_max = self.screen_width - self.frame_width - int(self.apple_block_height / 2)  # Using screen width to stay inside square area
            overlapping_snake = True
            while overlapping_snake:
                self.apple_block_react.centerx = np.random.randint(low=x_min, high=x_max, size=1)[0]
                self.apple_block_react.centery = np.random.randint(low=y_min, high=y_max, size=1)[0]
                for snake_block in range(len(self.snake_block_reacts)):
                    if pygame.Rect.colliderect(self.apple_block_react, self.snake_block_reacts[snake_block]):
                        overlapping_snake = True
                    else:
                        overlapping_snake = False

    def update_score(self):
        self.current_score += 10
        current_x, current_y = self.score_value_react.centerx, self.score_value_react.centery
        self.score_value_surface = self.score_board_font.render(str(self.current_score), True, self.text_color, None)
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
        if len(self.snake_block_reacts) > 1:
            for snake_body_block in range(1, len(self.snake_block_reacts)):
                history_index = snake_body_block * self.spawn_delay
                self.snake_block_reacts[snake_body_block].centerx = self.snake_head_history[history_index][0]
                self.snake_block_reacts[snake_body_block].centery = self.snake_head_history[history_index][1]

    def update_counters(self):
        pass

    def save_snake_head_history(self):
        self.snake_head_history.append([self.snake_block_reacts[0].centerx,
                                        self.snake_block_reacts[0].centery])

    def update_snake_head_history(self):
        history_length = len(self.snake_block_reacts) * self.spawn_delay
        if len(self.snake_head_history) > history_length:
            self.snake_head_history = self.snake_head_history[(len(self.snake_head_history) - history_length):]

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
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

    def snake_2_apple_collision_detection(self):
        if pygame.Rect.colliderect(self.apple_block_react, self.snake_block_reacts[0]):
            self.spawn_apple_flag = True
            self.spawn_snake_block_flag = True
            self.update_score()

    def in_game_render(self):
        # Rendering background
        self.display_surf.blit(self.background_surf, (0, 0))
        # Rendering snake
        for snake_block in self.snake_block_reacts:
            self.display_surf.blit(self.snake_block_surf, snake_block)
        # Rendering apple
        self.display_surf.blit(self.apple_block_surf, self.apple_block_react)
        # Rendering score text
        self.display_surf.blit(self.score_text_surface, self.score_text_react)
        # Rendering score value
        self.display_surf.blit(self.score_value_surface, self.score_value_react)
        pygame.display.flip()  # This is needed for image to show up ??

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self.running = False

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)

            self.update_snake_head_history()
            self.update_snake_head_position()
            self.snake_2_apple_collision_detection()

            if self.spawn_snake_block_flag:
                self.spawn_snake_block()

            if self.spawn_apple_flag:
                self.spawn_apple()

            self.save_snake_head_history()
            self.update_snake_body_position()

            self.update_counters()
            self.in_game_render()

        self.on_cleanup()


if __name__ == "__main__":
    theApp = SnakeApp()
    theApp.on_execute()
