# Tetress AI Agent - Monte Carlo Tree Search Implementation

## Overview

This project is designed to implement an AI agent for the game **Tetress**, a two-player, perfect-information board game where players take turns placing tetrominoes on an 11x11 toroidal board. The goal is to strategically block your opponent and clear rows or columns of tokens, thereby controlling the board. The game ends when a player can no longer place a valid piece or after 150 turns, whichever comes first.

### Game Description

**Tetress** is a competitive, tactical game where players (Red and Blue) alternate placing tetrominoes (Tetris-style pieces) on the board. Each tetromino consists of four connected tokens, and the player must ensure that at least one token is adjacent to an already placed token of the same color (except for the first turn). A player wins by preventing their opponent from placing a piece or having more tokens on the board when the game ends.

The game board has no real edges and behaves like a **torus**, meaning that positions at the edge of the grid wrap around to the opposite side. This unique mechanic increases the complexity of the game, as moves that seem isolated can actually impact the entire board.

## Project Objective

The main task is to design and implement an **AI agent** capable of playing Tetress by making intelligent decisions each turn. The AI uses **Monte Carlo Tree Search (MCTS)**, a popular algorithm for decision-making in complex board games, to simulate multiple possible outcomes and choose the best move. The MCTS agent aims to maximize its chances of winning by efficiently exploring the game tree, balancing exploration and exploitation during decision-making.

### Project Structure

The project consists of several main components:

1. **Node Class**: Represents each possible game state as nodes in the Monte Carlo Tree. This class tracks the state of the game, the action that led to the state, and statistics like the number of visits and rewards.
   
2. **Agent Class (MCTS AI)**: The core AI responsible for selecting and executing the best move using MCTS. This class handles:
   - **Action Selection**: Runs the MCTS algorithm to simulate possible game outcomes and pick the best action based on simulations.
   - **Rollout Simulations**: Randomly plays out the game from a given state to estimate its value.
   - **Backpropagation**: Updates the game tree with results from rollouts.
   
3. **Game Logic**: Implements the game rules, including legal move generation, board state updates, and piece placements according to the rules of Tetress.

## Key Features

- **Monte Carlo Tree Search (MCTS)**: The agent uses MCTS to explore different game states, evaluating each state's potential using random rollouts and backpropagation.
  
- **Legal Move Generation**: The AI ensures that each tetromino placement adheres to the game’s rules, including adjacency requirements and the toroidal nature of the board.

- **Evaluation Function**: Custom heuristic function that evaluates game states based on factors like:
  - Control of central positions on the board.
  - Coverage of tokens.
  - Clearing rows and columns, leading to opponent token removal.

- **Efficient Simulations**: The MCTS algorithm ensures the agent explores a diverse set of potential future states to optimize decision-making within the time limit.

## Skills Demonstrated

1. **Artificial Intelligence and Game Theory**: 
   - Use of MCTS for intelligent decision-making in a competitive game environment.
   - Application of game theory principles to manage adversarial interactions between players.
   
2. **Python Programming**:
   - Object-oriented design and structuring of the code to implement an AI agent.
   - Use of data structures like trees and heuristics for optimal game performance.
   
3. **Algorithm Design**:
   - Implementation of advanced game-playing algorithms, including MCTS and custom state evaluation heuristics.

4. **Strategic Gameplay**:
   - Development of strategies that balance offensive (blocking the opponent) and defensive (clearing lines) moves.
   - Use of the toroidal board mechanic to maximize influence across the game space.

## Conclusion

This project demonstrates the application of **Monte Carlo Tree Search (MCTS)** to build an intelligent agent capable of playing the Tetress game. The AI agent can make strategic decisions in real-time, adapting its playstyle to its opponent's actions and maximizing its control of the board. By leveraging simulation-based search, the agent offers a competitive challenge in the game, showcasing a range of skills in AI, game theory, and Python programming.
