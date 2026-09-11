import random
from enum import Enum
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

# (dx, dy) deltas for each action. y grows downward (row index increases).
ACTION_DELTAS = {
  Action.UP: (0, -1),
  Action.DOWN: (0, 1),
  Action.LEFT: (-1, 0),
  Action.RIGHT: (1, 0),
}

# This object manages the game state, storing things like the board and the
# snake and exposing methods like step(action), reset(), and get_state().
class GameState:
  def __init__(self, rows, columns):
    # Force even dimensions BEFORE allocating arrays. Even dimensions are
    # required later for the 2x2 super-cell Hamiltonian cycle, and allocating
    # after the bump keeps every array sized consistently with rows/columns.
    if rows % 2 == 1:
      rows += 1
    if columns % 2 == 1:
      columns += 1

    self.rows = rows
    self.columns = columns
    self.board_size = rows * columns

    # Grid array: one integer state per cell (Square.*.value).
    self.board = [Square.EMPTY.value] * self.board_size
    # Ring buffer: stores the board index of each occupied snake cell.
    self.snake = [0] * self.board_size

    self.head = 0
    self.tail = 0
    self.score = 1
    self.food = -1
    self.game_over = False
    self.won = False

    self.reset()

  # ---- pointer + coordinate helpers -------------------------------------

  # advance a ring-buffer pointer with modulo wrap-around.
  def increment_ptr(self, ptr: int) -> int:
    return (ptr + 1) % self.board_size

  # length of the snake = number of cells between tail and head inclusive.
  def length(self) -> int:
    return (self.head - self.tail) % self.board_size + 1

  def to_index(self, x: int, y: int) -> int:
    return y * self.columns + x

  def to_xy(self, index: int):
    return index % self.columns, index // self.columns

  # ---- game lifecycle ---------------------------------------------------

  # reset the board to a default single-cell snake plus one apple.
  def reset(self):
    for i in range(self.board_size):
      self.board[i] = Square.EMPTY.value

    start = self.to_index(self.columns // 2, self.rows // 2)
    self.head = 0
    self.tail = 0
    self.snake[0] = start
    self.board[start] = Square.SNAKE.value
    self.score = 1
    self.game_over = False
    self.won = False
    self.spawn_food()

  # place an apple on a random empty cell. If none remain, the board is full
  # and the game is won.
  def spawn_food(self):
    empties = [i for i in range(self.board_size)
               if self.board[i] == Square.EMPTY.value]
    if not empties:
      self.food = -1
      self.won = True
      self.game_over = True
      return
    self.food = random.choice(empties)
    self.board[self.food] = Square.FOOD.value

  # perform a single move of the snake. Returns True if the snake is still
  # alive after the move, False if the move ended the game.
  def step(self, action: Action):
    if self.game_over:
      return False

    head_index = self.snake[self.head]
    hx, hy = self.to_xy(head_index)
    dx, dy = ACTION_DELTAS[action]
    nx, ny = hx + dx, hy + dy

    # bounds check: no wrapping across edges.
    if nx < 0 or nx >= self.columns or ny < 0 or ny >= self.rows:
      self.game_over = True
      return False

    new_index = self.to_index(nx, ny)
    eating = self.board[new_index] == Square.FOOD.value
    tail_index = self.snake[self.tail]

    # self-collision. Moving into the current tail cell is legal on a
    # non-eating move because the tail vacates that cell this turn.
    if self.board[new_index] == Square.SNAKE.value:
      if not (new_index == tail_index and not eating):
        self.game_over = True
        return False

    if not eating:
      # vacate the tail first so it can't erase the freshly written head.
      self.board[tail_index] = Square.EMPTY.value
      self.tail = self.increment_ptr(self.tail)

    # advance the head.
    self.head = self.increment_ptr(self.head)
    self.snake[self.head] = new_index
    self.board[new_index] = Square.SNAKE.value

    if eating:
      self.score += 1
      self.spawn_food()

    return not self.game_over

  # ---- debugging --------------------------------------------------------

  def print_state(self):
    for row in range(self.rows):
      print("|", end="")
      for col in range(self.columns):
        cell = self.board[row * self.columns + col]
        if cell == Square.SNAKE.value:
          print("S", end="")
        elif cell == Square.FOOD.value:
          print("A", end="")
        else:
          print(".", end="")
      print("|")
    print(f"score={self.score} game_over={self.game_over} won={self.won}")

# This is the ai class that plays the game
class Agent:
  pass

# This object controls the main game loop and rendering
class GameController:
  pass


def main():
  pygame.init()

  # Phase 2, Step 3: verify the engine with a hardcoded input sequence on a
  # small board. A fixed seed keeps apple placement deterministic.
  random.seed(0)
  game_state = GameState(6, 6)

  print("initial state:")
  game_state.print_state()

  sequence = [
    Action.RIGHT, Action.RIGHT, Action.DOWN, Action.DOWN,
    Action.LEFT, Action.LEFT, Action.UP,
  ]
  for action in sequence:
    alive = game_state.step(action)
    print(f"\nafter {action.name} (alive={alive}):")
    game_state.print_state()

if __name__ == "__main__":
  main()
