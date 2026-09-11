# Snake AI Architecture & Implementation Plan

This document outlines the step-by-step implementation for a perfect-play Snake AI. The architecture avoids heavy OOP overhead in favor of a data-oriented approach to maximize simulation speed, and relies on graph theory (Hamiltonian cycles with shortcut heuristics) rather than pure reinforcement learning to guarantee survival.

## Phase 1: Data Structures & State Management
Before rendering anything, build the underlying memory structures. The goal is zero memory allocation during the game loop.

*   **Step 1: The Grid Array**
    *   Implement the board as a flat 1D array of integers (e.g., size 400 for a 20x20 grid).
    *   Define integer constants for states: `0 = EMPTY`, `1 = APPLE`, `2 = SNAKE_BODY`.
*   **Step 2: The Ring Buffer (Snake Body)**
    *   Allocate a second 1D array of the same size to act as the circular buffer.
    *   Implement the `head_ptr` and `tail_ptr` integers to track indices.
    *   Create helper methods to advance pointers using modulo arithmetic (`(ptr + 1) % board_size`).
*   **Step 3: Coordinate Translation**
    *   Write utility functions to translate 2D `(x, y)` coordinates to 1D indices (`index = y * width + x`) and vice versa. This allows you to handle directional math (Up = `-width`, Down = `+width`, Left = `-1`, Right = `+1`) cleanly.

## Phase 2: The Core Game Engine
Build a headless, deterministic game environment that can run silently at maximum CPU speed or output to a simple UI for debugging.

*   **Step 1: Movement & Digestion Logic**
    *   Implement the step logic: calculate the new head index, update the Grid Array, and write to the Ring Buffer.
    *   Implement the apple consumption logic (advance `head_ptr` but keep `tail_ptr` stationary for one turn).
*   **Step 2: Collision Detection**
    *   Implement bounds checking (preventing wrapping across the left/right edges when using 1D index math).
    *   Check for self-collision by querying the Grid Array before finalizing a move.
*   **Step 3: The Game Loop & API**
    *   Structure the engine to accept a generic `step(direction)` command.
    *   Verify the engine is bulletproof by hardcoding a simple, repeating sequence of inputs.

## Phase 3: Hamiltonian Cycle Generation
Treat the board as an undirected graph to generate the baseline survival path.

*   **Step 1: Super-Cell Partitioning**
    *   Logically divide the board into 2x2 blocks (a 20x20 grid becomes a 10x10 graph of nodes).
*   **Step 2: Minimum Spanning Tree (MST)**
    *   Implement a randomized Depth-First Search (DFS) or Prim's algorithm to generate a spanning tree connecting every 2x2 super-cell without forming any loops.
*   **Step 3: Boundary Tracing**
    *   Write an algorithm to trace the outer perimeter of the MST.
    *   Output the result as a static 1D array (the "Cycle Array"), where the value at each index represents its sequential order in the loop (0 to `board_size - 1`). 

## Phase 4: The AI Agent & Shortcut Engine
Integrate the decision-making logic that maps the 2D grid actions to the 1D Cycle Array constraints.

*   **Step 1: Cycle Following (The Fallback)**
    *   Implement the baseline AI: look at adjacent squares, find the one whose Cycle Array value is exactly `current_head_value + 1` (accounting for modulo wrap-around), and move there.
*   **Step 2: Shortcut Evaluation**
    *   For every adjacent square, calculate the 1D distance to the Apple.
    *   Calculate the 1D distance to the Tail.
*   **Step 3: The Safety Constraints**
    *   Apply the two core rules before accepting a shortcut:
        1. The target square must be between the Head and the Apple on the 1D cycle.
        2. The distance from the target square to the Tail on the 1D cycle must be strictly greater than the snake's current length.
*   **Step 4: Digestion Buffer Handling**
    *   Add an edge-case rule: if an apple was just eaten, temporarily treat the tail as stationary in distance calculations to prevent rear-end collisions.

## Phase 5: Tuning & Advanced Pathing
Once the bot is playing safely, optimize its efficiency.

*   **Step 1: A* Search Integration (Optional)**
    *   Instead of just checking the 4 immediate neighbors, implement an A* pathfinding algorithm to find the absolute shortest 2D path to the apple.
    *   Use the 1D Cycle Array rules from Phase 4 as strict constraints for expanding nodes in the A* search space.
*   **Step 2: Late-Game Thresholds**
    *   Implement a capacity check. When the snake occupies ~75-80% of the board, disable the shortcut engine to prevent complex entrapment scenarios. Force the AI to revert to the Phase 4 Step 1 strict cycle following to safely close out the game.