import numpy as np
import torch
import pygame
from Agent import *


class FakeRect:
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
        self.size = (self._height, self._width)

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
        return FakeRect(width=self._width,
                        height=self._height,
                        centerx=self._centerx,
                        centery=self._centery,
                        left=self._left,
                        right=self._right,
                        top=self._top,
                        bottom=self._bottom)


class PygameText:
    def __init__(self,
                 filename: str,
                 text: str,
                 text_size: int) -> None:
        self.filename = filename
        self.text = text
        self.text_size = text_size

        self.color = (255, 255, 255)  # White
        self.font = pygame.font.Font(self.filename, self.text_size)
        self.surface = self.font.render(self.text, True, self.color, None)
        self.rect = self.surface.get_rect()

    def set_position(self, left: int | float, top: int | float) -> None:
        self.rect.left, self.rect.top = left, top

    def get_position(self) -> tuple[int | float, int | float]:
        return self.rect.left, self.rect.top

    def set_text_color(self, RGB: tuple[int, int, int]) -> None:
        self.color = RGB
        self.surface = self.font.render(self.text, True, self.color, None)

    def get_text_color(self) -> tuple[int, int, int]:
        return self.color



class HyperParameters:
    def __init__(self, batch_size: int, gamma: float, eps_0: float,
                 eps_min: float, eps_decay_rate: float, target_update_freq: int,
                 learning_rate: float, memory_size: int, n_episodes: int):
        self.batch_size = batch_size
        self.gamma = gamma
        self.initial_epsilon = eps_0
        self.minimal_epsilon = eps_min
        self.epsilon_decay_rate = eps_decay_rate
        self.target_update_frequency = target_update_freq

        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.n_episodes = n_episodes

    def __str__(self):
        string_repr = "####### Hyperparameters ####### : \n"
        for key in list(self.__dict__.keys()):
            string_repr += str(key) + ": " + str(self.__dict__[key]) + "\n "
        return string_repr


class TrainingData:
    def __init__(self, scores: np.ndarray, steps: np.ndarray, eps: np.ndarray):
        self.scores = scores
        self.steps = steps
        self.eps = eps

    def get_formatted_data(self):
        formatted_data = [self.steps, self.scores, self.eps]
        return formatted_data


def save_session(filename: str,
                 note: str,
                 params: HyperParameters,
                 agent: Agent,
                 data: TrainingData):
    file = open(file=filename, mode='w')
    file.write("\n########################################################################## \n")
    file.write("################################ Settings ################################ \n")
    file.write("########################################################################## \n\n")
    file.write(note + "\n")
    file.write(params.__str__() + "\n")
    file.write(agent.__str__() + "\n")
    file.write("\n########################################################################## \n")
    file.write("################################## DATA ################################## \n")
    file.write("########################################################################## \n")
    file.write("{: >20} {: >20} {: >20}".format("steps:", "scores:", "epsilon:")+"\n")
    for row in np.array(data.get_formatted_data()).T:
        file.write("{: >20} {: >20} {: >20}".format(*list(row))+"\n")
    file.close()

