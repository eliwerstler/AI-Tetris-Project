from referee.game import PlayerColor, Action, PlaceAction, Coord
from referee.game.constants import BOARD_N
from referee.game.pieces import PieceType, create_piece
from typing import List, Dict, Tuple, Optional
import time
import random
import math


# Define a class for the nodes in the Monte Carlo Tree Search
class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # The state of the game at this node
        self.parent = parent  # The parent node
        self.action = action  # The action that led to this node
        self.children = []  # The children of this node
        self.visits = 0  # Number of times this node has been visited
        self.value = 0  # Value of this node

    # Check if the node is fully expanded (i.e., all possible actions have been tried)
    def is_fully_expanded(self, agent, color):
        return len(self.children) == len(agent.get_legal_actions(self.state, color))

    # Select the best child node using the UCB1 formula
    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.value / child.visits)
            + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return (
            self.children[choices_weights.index(max(choices_weights))]
            if choices_weights
            else None
        )


# Define the Agent class
class Agent:
    def __init__(self, color: PlayerColor, **referee: dict):
        self._color = color  # The color of the player
        self._state = [[None for _ in range(BOARD_N)] for _ in range(BOARD_N)]
        self._opponent_color = (
            PlayerColor.RED if self._color == PlayerColor.BLUE else PlayerColor.BLUE
        )
        print(f"Initializing Agent as {self._color}")

    # Function to determine the action to take
    def action(self, **referee: dict) -> Action:
        start_time = time.time()
        time_limit = 0.03  # Set a time limit for the search
        root = Node(state=self._state)

        # Perform the MCTS while within the time limit
        while time.time() - start_time < time_limit:
            leaf = self.tree_policy(root)
            simulation_result = self.rollout(leaf.state)
            self.backpropagate(leaf, simulation_result)

        action = self.best_action(root)
        print(f"Chosen action: {action}")
        return action if action is not None else self.get_fallback_action()

    # Function to update the internal state based on the action taken 50 - 46
    def update(self, color: PlayerColor, action: Action, **referee: dict):
        place_action: PlaceAction = action
        for coord in place_action.coords:
            self._state[coord.r][coord.c] = color
        self.clear_lines()

    # Function to select a leaf node for expansion
    def tree_policy(self, node: Node):
        while not self.is_terminal(node.state):
            if not node.is_fully_expanded(self, self._color):
                return self.expand(node)
            else:
                node = node.best_child()
        return node

    # Function to expand a node by adding a child node for an unexplored action
    def expand(self, node: Node):
        legal_actions = self.get_legal_actions(node.state, self._color)
        for action in legal_actions:
            if action not in [child.action for child in node.children]:
                new_state = self.apply_action(node.state, action, self._color)
                child_node = Node(state=new_state, parent=node, action=action)
                node.children.append(child_node)
                return child_node
        return node

    # Function to simulate a random playout from a given state
    def rollout(self, state):
        current_state = [row[:] for row in state]
        current_color = self._color

        while not self.is_terminal(current_state):
            legal_actions = self.get_legal_actions(current_state, current_color)
            if not legal_actions:
                break
            action = random.choice(legal_actions)
            current_state = self.apply_action(current_state, action, current_color)
            current_color = (
                self._opponent_color if current_color == self._color else self._color
            )

        return self.evaluate(current_state)

    # Function to propagate the results of a simulation up the tree
    def backpropagate(self, node: Node, result):
        while node is not None:
            node.visits += 1
            node.value += result
            node = node.parent

    # Function to select the best action to take from the root node
    def best_action(self, root: Node):
        best_child = root.best_child(c_param=0)
        if best_child and self.is_legal_move(
            root.state, best_child.action, self._color
        ):
            return best_child.action
        legal_actions = self.get_legal_actions(root.state, self._color)
        if legal_actions:
            fallback_action = random.choice(legal_actions)
            print(f"Fallback action: {fallback_action}")
            return fallback_action
        else:
            print("No legal actions available!")
            return None

    # Function to get a fallback action if no valid action is found
    def get_fallback_action(self):
        legal_actions = self.get_legal_actions(self._state, self._color)
        return random.choice(legal_actions) if legal_actions else None

    # Function to apply an action to a given state
    def apply_action(self, state, action: PlaceAction, color: PlayerColor):
        new_state = [row[:] for row in state]
        for coord in action.coords:
            new_state[coord.r][coord.c] = color
        return self.clear_lines_in_state(new_state)

    # Function to check if a state is terminal (no legal moves left)
    def is_terminal(self, state):
        return not any(
            self.is_legal_shape(state, r, c, piece_type, self._color)
            for r in range(BOARD_N)
            for c in range(BOARD_N)
            for piece_type in PieceType
        )

    # Function to evaluate a state (used in the rollout)
    def evaluate(self, state):
        """
        my_pieces = sum(cell == self._color for row in state for cell in row)
        opponent_pieces = sum(
            cell == self._opponent_color for row in state for cell in row
        )
        return my_pieces - opponent_pieces
        """
        score = 0

        opponent_line_removal_score = 0
        player_line_penalty = 0

        # Check each row and column for potential completion
        for i in range(BOARD_N):
            player_in_row, opponent_in_row = 0, 0
            player_in_col, opponent_in_col = 0, 0

            for j in range(BOARD_N):
                if state[i][j] == self._color:
                    player_in_row += 1
                elif state[i][j] == self._opponent_color:
                    opponent_in_row += 1

                if state[j][i] == self._color:
                    player_in_col += 1
                elif state[j][i] == self._opponent_color:
                    opponent_in_col += 1

        # Evaluate the row and column for line completion
        if player_in_row + opponent_in_row == BOARD_N:
            if opponent_in_row > player_in_row:
                opponent_line_removal_score += (
                    opponent_in_row * 10
                )  # Weight by number of opponent's tiles
            player_line_penalty += player_in_row * 5

        if player_in_col + opponent_in_col == BOARD_N:
            if opponent_in_col > player_in_col:
                opponent_line_removal_score += (
                    opponent_in_col * 10
                )  # Weight by number of opponent's tiles
            player_line_penalty += player_in_col * 5

        score += opponent_line_removal_score - player_line_penalty

        coverage_score = 0
        central_control_score = 0
        for i in range(BOARD_N):
            for j in range(BOARD_N):
                if state[i][j] != 0:
                    coverage_score += 1
                    if i in range(BOARD_N // 3, 2 * BOARD_N // 3) and j in range(
                        BOARD_N // 3, 2 * BOARD_N // 3
                    ):
                        central_control_score += (
                            1  # more weight if within the central area
                        )

        score += coverage_score * 5
        score += central_control_score * 10  # Central positions are more valuable

        return score

    # Function to get all legal actions for a given state and player color
    def get_legal_actions(self, state, color: PlayerColor) -> List[PlaceAction]:
        legal_actions = []
        for r in range(BOARD_N):
            for c in range(BOARD_N):
                for piece_type in PieceType:
                    if self.is_legal_shape(state, r, c, piece_type, color):
                        piece = create_piece(piece_type, Coord(r, c))
                        legal_actions.append(PlaceAction(*piece.coords))
        return legal_actions

    # Function to check if a piece placement is legal
    def is_legal_shape(
        self, state, r: int, c: int, piece_type: PieceType, color: PlayerColor
    ) -> bool:
        try:
            piece = create_piece(piece_type, Coord(r, c))
            coords = piece.coords
            if all(
                0 <= coord.r < BOARD_N
                and 0 <= coord.c < BOARD_N
                and state[coord.r][coord.c] is None
                for coord in coords
            ):
                if self.has_neighbor(state, coords, color) or self.turn_count < 2:
                    return True
        except ValueError:
            return False
        return False

    # Function to check if the piece has a neighboring piece of the same color
    def has_neighbor(self, state, coords, color):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for coord in coords:
            for dr, dc in directions:
                nr, nc = coord.r + dr, coord.c + dc
                if 0 <= nr < BOARD_N and 0 <= nc < BOARD_N:
                    if state[nr][nc] == color:
                        return True
        return False

    # Function to check if a move is legal
    def is_legal_move(self, state, action: PlaceAction, color: PlayerColor) -> bool:
        coords = action.coords
        if all(
            0 <= coord.r < BOARD_N
            and 0 <= coord.c < BOARD_N
            and state[coord.r][coord.c] is None
            for coord in coords
        ):
            if self.has_neighbor(state, coords, color) or self.turn_count < 2:
                return True
        return False

    # Function to clear completed lines in the current state
    def clear_lines(self):
        new_state = self.clear_lines_in_state(self._state)
        self._state = new_state

    # Function to clear completed lines in a given state
    def clear_lines_in_state(self, state):
        new_state = [row[:] for row in state]

        # Check for completed rows
        for r in range(BOARD_N):
            if all(cell is not None for cell in state[r]):
                for c in range(BOARD_N):
                    new_state[r][c] = None

        # Check for completed columns
        for c in range(BOARD_N):
            if all(state[r][c] is not None for r in range(BOARD_N)):
                for r in range(BOARD_N):
                    new_state[r][c] = None

        return new_state

    # Property to get the current turn count
    @property
    def turn_count(self) -> int:
        return sum(cell is not None for row in self._state for cell in row) // 4
