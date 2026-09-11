from typing import List
import pygame


class Square(Enum):
  EMPTY = 0
  FOOD = 1
  SNAKE = 2

class Action(Enum):
  UP = 0
  DOWN = 1
  LEFT = 2
  RIGHT = 3

# This object manages the game stat, storing things like the board and the snake
# and exposing methods like step(action), reset(), and get_state()
class GameState:
  def __init__(self, rows, columns):
    self.rows = rows
    self.columns = columns
    self.board_size = rows * columns
    self.snake = [0] * (rows * columns)
    self.board = [0] * (rows * columns)
    self.head = -1 # TODO
    self.tail = -1 # TODO
    self.score = 1
    if self.rows % 2 == 1:
      self.rows += 1
    if self.columns % 2 == 1:
      self.columns += 1

  # helper function to use with head and tail pointer locations in array. 
  def increment_ptr(ptr : int):
      return (ptr + 1) % board_size

  def print_state():
    for row in self.rows:
      print("|")
      for col in self.columns:
        if self.board[row][col] == Square.SNAKE:
          print("S")
        elif self.board[row][col] == Square.FOOD:
          print("A")
        else: 
          print(".")
      print("|")
  # perform a single move of the snake
  def step(self, action : Action):
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




def main():
  pygame.init()
  game_state = GameState(10, 10)
  agent = Agent()
  controller = GameController(game_state, agent)
  game_state.print_state()

if __name__ == "__main__":
  main()