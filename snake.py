from typing import List
import pygame


# This object manages the game state, storing things like the board and the snake
# and exposing methods like step(action), reset(), and get_state()
class GameState:
  def __init__(self, rows, columns):
    self.rows = rows
    self.columns = columns
    self.snake = []
    self.board = []
    self.head = -1 # TODO
    self.tail = -1 # TODO
    self.score = 1

  # perform a single move of the snake
  def step(self, action):
    pass
  # reset the board to a default board
  def reset(self):
    pass

# This is the ai class that plays the game
class Agent:
  pass

# This object controls the main game loop and rendering
class GameController:
  pass