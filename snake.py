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

# Maps arrow / WASD keys to actions.
KEY_ACTIONS = {
  pygame.K_UP: Action.UP,
  pygame.K_w: Action.UP,
  pygame.K_DOWN: Action.DOWN,
  pygame.K_s: Action.DOWN,
  pygame.K_LEFT: Action.LEFT,
  pygame.K_a: Action.LEFT,
  pygame.K_RIGHT: Action.RIGHT,
  pygame.K_d: Action.RIGHT,
}

# Actions that are direct reversals of each other. A snake can't turn 180
# degrees into its own neck.
OPPOSITE = {
  Action.UP: Action.DOWN,
  Action.DOWN: Action.UP,
  Action.LEFT: Action.RIGHT,
  Action.RIGHT: Action.LEFT,
}

# Colors.
COLOR_BG = (18, 18, 18)
COLOR_GRID = (32, 32, 32)
COLOR_SNAKE = (60, 200, 90)
COLOR_HEAD = (120, 240, 140)
COLOR_FOOD = (220, 70, 70)

# This object controls the main game loop and rendering.
class GameController:
  def __init__(self, rows=20, columns=20, cell_size=24, fps=10):
    self.cell_size = cell_size
    self.fps = fps
    self.game = GameState(rows, columns)
    # use the (possibly bumped-to-even) dimensions from the game state.
    self.width = self.game.columns * cell_size
    self.height = self.game.rows * cell_size
    self.direction = Action.RIGHT
    self.screen = None
    self.clock = None
    self.font = None

  def run(self):
    pygame.init()
    self.screen = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption("Snake")
    self.clock = pygame.time.Clock()
    self.font = pygame.font.SysFont(None, 32)

    running = True
    while running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False
        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            running = False
          elif event.key == pygame.K_r and self.game.game_over:
            self.game.reset()
            self.direction = Action.RIGHT
          elif event.key in KEY_ACTIONS:
            new_dir = KEY_ACTIONS[event.key]
            # ignore reversals unless the snake is length 1.
            if self.game.length() == 1 or new_dir != OPPOSITE[self.direction]:
              self.direction = new_dir

      if not self.game.game_over:
        self.game.step(self.direction)

      self.render()
      self.clock.tick(self.fps)

    pygame.quit()

  def render(self):
    self.screen.fill(COLOR_BG)
    cs = self.cell_size

    # subtle grid lines.
    for x in range(0, self.width, cs):
      pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, self.height))
    for y in range(0, self.height, cs):
      pygame.draw.line(self.screen, COLOR_GRID, (0, y), (self.width, y))

    head_index = self.game.snake[self.game.head]
    for i in range(self.game.board_size):
      cell = self.game.board[i]
      if cell == Square.EMPTY.value:
        continue
      x, y = self.game.to_xy(i)
      rect = pygame.Rect(x * cs, y * cs, cs, cs)
      if cell == Square.FOOD.value:
        pygame.draw.rect(self.screen, COLOR_FOOD, rect)
      elif cell == Square.SNAKE.value:
        color = COLOR_HEAD if i == head_index else COLOR_SNAKE
        pygame.draw.rect(self.screen, color, rect)

    score_surf = self.font.render(f"Score: {self.game.score}", True, (230, 230, 230))
    self.screen.blit(score_surf, (8, 6))

    if self.game.game_over:
      msg = "You win! " if self.game.won else "Game over "
      over_surf = self.font.render(msg + "- press R to restart", True, (255, 255, 255))
      rect = over_surf.get_rect(center=(self.width // 2, self.height // 2))
      self.screen.blit(over_surf, rect)

    pygame.display.flip()


def main():
  GameController(rows=20, columns=20, cell_size=24, fps=10).run()

if __name__ == "__main__":
  main()
