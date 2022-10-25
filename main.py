import pygame
from pygame.locals import *
import numpy as np
from copy import deepcopy

# TODO: fix problem with snake head hitting two apples within 'self.spawn_delay' nr. of frames (quick fix. by distance of apple spawn)


class SnakeApp:
    def __init__(self):
        self.running = True
        self.display_surf = None
        self.background_surf = None
        self.screen_size = self.screen_width, self.screen_height = 714, 777
        self.frame_width = int((self.screen_width - 700) / 2)+2
        self.fps = pygame.time.Clock()

        self.snake_block_surf = None
        self.max_nr_snake_blocks = 400
        self.snake_block_reacts = np.zeros(shape=(self.max_nr_snake_blocks,), dtype=object)
        self.current_snake_blocks = 1
        self.snake_block_size = self.snake_block_width, self.snake_block_height = 35, 35

        self.snake_velocity = 2  # pixels pr. frame
        self.snake_head_direction = None
        self.snake_head_history = []
        self.spawn_delay = int(self.snake_block_height/self.snake_velocity)
        self.spawn_snake_block_flag = False

        self.apple_block_surf = None
        self.apple_block_react = None
        self.apple_block_size = self.apple_block_width, self.apple_block_height = 35, 35
        self.spawn_apple_flag = True
        self.game_over = False

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

        self.game_over_font = pygame.font.Font("media/arcade_classic.ttf", 35)
        self.game_over_background_surf = None
        self.game_over_text_surface = self.game_over_font.render("Game Over", True, self.text_color, None)
        self.game_over_text_react = self.game_over_text_surface.get_rect()
        self.game_over_text_react.centerx = int(self.screen_width/2) + 3
        self.game_over_text_react.centery = int(self.screen_height/2)
        self.game_over_anim_duration = 25
        self.game_over_anim_counter = 0
        self.game_over_position = "down"

        # light shade of the button
        self.restart_button_color_light = (170, 170, 170)
        # dark shade of the button
        self.restart_button_color_dark = (100, 100, 100)
        self.restart_button_width = 240
        self.restart_button_height = 60
        self.restart_button_dims = [self.screen_width / 2 - self.restart_button_width/2,
                                    self.screen_height / 2 + int(1.3*self.restart_button_height),
                                    self.restart_button_width,
                                    self.restart_button_height]

        self.restart_font = pygame.font.Font("media/arcade_classic.ttf", 30)
        self.restart_text_surface = self.restart_font.render("restart", True, self.text_color, None)
        self.restart_text_react = self.restart_text_surface.get_rect()
        self.restart_text_react.centerx = int(self.screen_width/2) + 3
        self.restart_text_react.centery = int(self.screen_height/2) + int(1.85*self.restart_button_height)

    def on_init(self):
        # Initializing pygame and loading in graphics for background
        pygame.init()
        self.running = True
        self.display_surf = pygame.display.set_mode(size=self.screen_size,
                                                    flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self.background_surf = pygame.image.load("media/background.png").convert()
        self.game_over_background_surf = pygame.image.load("media/background.png").convert()

        # Loading in graphics for snake
        self.snake_block_surf = pygame.image.load("media/snake_block.png").convert_alpha()
        self.snake_block_reacts[self.current_snake_blocks-1] = self.snake_block_surf.get_rect()
        self.snake_block_reacts[self.current_snake_blocks-1].centerx = int(self.screen_width/2)
        self.snake_block_reacts[self.current_snake_blocks-1].centery = int(self.screen_height/2)

        # Loading in graphics for apple
        self.apple_block_surf = pygame.image.load("media/apple.png").convert_alpha()
        self.apple_block_react = self.snake_block_surf.get_rect()

    def spawn_snake_block(self):
        self.spawn_snake_block_flag = False
        snake_block = self.snake_block_surf.get_rect()
        index = self.current_snake_blocks-1
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
        if self.spawn_apple_flag:
            self.spawn_apple_flag = False
            x_min = self.frame_width + int(self.apple_block_width / 2)
            x_max = self.screen_width - self.frame_width - int(self.apple_block_width / 2)
            y_min = self.frame_width + int(self.apple_block_height / 2)
            y_max = self.screen_width - self.frame_width - int(self.apple_block_height / 2)  # Using screen width to stay inside square area
            snake_head = self.snake_block_reacts[0]
            overlapping_snake = True
            while overlapping_snake:
                self.apple_block_react.centerx = np.random.randint(low=x_min, high=x_max, size=1)[0]
                self.apple_block_react.centery = np.random.randint(low=y_min, high=y_max, size=1)[0]
                for snake_block in range(self.current_snake_blocks):
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
        if not self.snake_2_wall_collision_detection():
            if self.snake_head_direction == "right":
                self.snake_block_reacts[0] = self.snake_block_reacts[0].move(self.snake_velocity, 0)
            elif self.snake_head_direction == "left":
                self.snake_block_reacts[0] = self.snake_block_reacts[0].move(-self.snake_velocity, 0)
            elif self.snake_head_direction == "up":
                self.snake_block_reacts[0] = self.snake_block_reacts[0].move(0, -self.snake_velocity)
            elif self.snake_head_direction == "down":
                self.snake_block_reacts[0] = self.snake_block_reacts[0].move(0, self.snake_velocity)

    def update_snake_body_position(self):
        if not self.snake_2_wall_collision_detection():
            if self.current_snake_blocks > 1:
                for snake_body_block in range(1, self.current_snake_blocks):
                    history_index = snake_body_block * self.spawn_delay
                    history_len = len(self.snake_head_history) - 1
                    self.snake_block_reacts[snake_body_block].centerx = self.snake_head_history[history_len - history_index][0]
                    self.snake_block_reacts[snake_body_block].centery = self.snake_head_history[history_len - history_index][1]

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

    def snake_2_wall_collision_detection(self):
        x_min, x_max = self.frame_width, self.screen_width-self.frame_width
        y_min, y_max = self.frame_width, self.screen_width-self.frame_width
        snake_head = self.snake_block_reacts[0]
        if snake_head.left < x_min or snake_head.right > x_max:
            self.game_over = True
            return True
        elif snake_head.bottom > y_max or snake_head.top < y_min:
            self.game_over = True
            return True
        return False

    def snake_2_snake_collision_detection(self):
        if self.current_snake_blocks > 1:
            snake_head = self.snake_block_reacts[0]
            for snake_body_index in range(1, self.current_snake_blocks):
                snake_body = self.snake_block_reacts[snake_body_index]
                dist = np.sqrt((snake_head.centerx - snake_body.centerx)**2 + (snake_head.centery - snake_body.centery)**2)
                if dist < 0.72 * self.snake_block_width:
                    self.game_over = True

    def update_game_over_react(self):
        """ Animating game over text """
        if self.game_over_anim_counter == self.game_over_anim_duration:
            self.game_over_anim_counter = 0
            if self.game_over_position == 'down':
                self.game_over_text_react.centery += 5
                self.game_over_position = 'up'
            else:
                self.game_over_text_react.centery -= 5
                self.game_over_position = 'down'

    def game_over_reset(self):
        self.game_over = False
        self.snake_head_direction = None
        self.current_snake_blocks = 1
        self.current_score = 0
        current_x, current_y = self.score_value_react.centerx, self.score_value_react.centery
        self.score_value_surface = self.score_board_font.render(str(self.current_score), True, self.text_color, None)
        self.score_value_react = self.score_value_surface.get_rect()
        self.score_value_react.centerx, self.score_value_react.centery = current_x, current_y
        self.snake_block_reacts = np.zeros(shape=(self.max_nr_snake_blocks,), dtype=object)
        self.snake_block_reacts[self.current_snake_blocks-1] = self.snake_block_surf.get_rect()
        self.snake_block_reacts[self.current_snake_blocks-1].centerx = int(self.screen_width/2)
        self.snake_block_reacts[self.current_snake_blocks-1].centery = int(self.screen_height/2)

    def in_game_render(self):
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
        pygame.display.flip()  # This is needed for image to show up ??

    def game_over_render(self):
        # Rendering background
        self.display_surf.blit(self.game_over_background_surf, (0, 0))
        self.display_surf.blit(self.game_over_text_surface, self.game_over_text_react)
        self.display_surf.blit(self.restart_text_surface, self.restart_text_react)
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

            if not self.game_over:
                self.update_snake_head_history()
                self.update_snake_head_position()
                self.snake_2_apple_collision_detection()
                self.snake_2_snake_collision_detection()

                if self.spawn_snake_block_flag:
                    self.spawn_snake_block()

                if self.spawn_apple_flag:
                    self.spawn_apple()

                self.save_snake_head_history()
                self.update_snake_body_position()

                self.in_game_render()
            else:
                mouse_position = pygame.mouse.get_pos()
                if self.restart_button_dims[0] <= mouse_position[0] <= self.restart_button_dims[
                    0] + self.restart_button_width \
                        and self.restart_button_dims[1] <= mouse_position[1] <= self.restart_button_dims[
                    1] + self.restart_button_height:
                    pygame.draw.rect(self.game_over_background_surf, self.restart_button_color_light,
                                     self.restart_button_dims)
                    left, middle, right = pygame.mouse.get_pressed()
                    if left:
                        self.game_over_reset()
                else:
                    pygame.draw.rect(self.game_over_background_surf, self.restart_button_color_dark,
                                     self.restart_button_dims)

                self.game_over_render()
                self.update_game_over_react()
                self.game_over_anim_counter += 1

        self.on_cleanup()


if __name__ == "__main__":
    theApp = SnakeApp()
    theApp.on_execute()
