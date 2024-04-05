import math
import random
import time

from board_utils import get_empty_positions, clone_board, check_board_status, IN_PROGRESS, get_potential_moves, is_empty
from gomoku_model import GomokuAI

INF = 2 ** 32 - 1
WIN_SCORE = 10
THINKING_TIME = 2000


def ucb(node):
    return INF if node.visits == 0 else node.win_score / node.visits + 2 * math.sqrt(
        math.log(node.parent.visits) / node.visits)


def best_child_key(child):
    if child.visits == 0:
        return -INF
    return child.win_score / child.visits


def opponent(player):
    return 3 - player


class State:
    def __init__(self, board, player, move=None, parent=None):
        self.parent = parent
        self.children = []
        self.player = player
        self.move = move
        self.visits = 0
        self.win_score = 0
        self.board = board

    def clone(self):
        clone = State(self.board, self.player, self.move, self.parent)
        clone.children = [child for child in self.children]
        clone.visits = self.visits
        clone.win_score = self.win_score
        clone.board = clone_board(self.board)
        return clone

    def get_random_child(self):
        if len(self.children) == 0:
            return None
        return random.choice(self.children)

    def get_best_child(self):
        return max(self.children, key=best_child_key)

    def get_child_with_best_ucb(self):
        return max(self.children, key=ucb)

    def random_play(self):
        self.player = opponent(self.player)
        pos = random.choice(get_potential_moves(self.board))
        self.board[pos[0]][pos[1]] = self.player

    def __str__(self):
        return f'{super.__str__(self)} : {self.win_score} / {self.visits}'


class GomokuMCTS(GomokuAI):
    def __init__(self, player, thinking_time=5000):
        self.name = "MCTS"
        self.root = None
        self.player = player
        global THINKING_TIME
        THINKING_TIME = thinking_time

    def calculate_move(self, board):
        if is_empty(board):
            padding = 1
            move = [random.randint(padding, len(board) - 1 - padding),
                    random.randint(padding, len(board[0]) - 1 - padding),
                    0]
            print(self.player, ':', move)
            return move

        if self.root is None:
            self.root = State(board, self.player)
        else:
            find_result = [b for b in self.root.children if b == board]
            if len(find_result) == 0:
                self.root = State(board, self.player)
            else:
                self.root = find_result[0]
                self.root.parent = None

        start_time = time.perf_counter()
        while int(round((time.perf_counter() - start_time) * 1000)) <= THINKING_TIME:
            selected_node = self.select()
            if check_board_status(selected_node.board) == IN_PROGRESS:
                self.expand(selected_node)
            explored_node = selected_node
            if len(selected_node.children) > 0:
                explored_node = selected_node.get_random_child()
            status = self.simulate(explored_node)
            self.back_propagation(explored_node, status)

        self.root = self.root.get_best_child()
        self.root.parent = None
        print(self.player, ':', [self.root.move[0], self.root.move[1], self.root.win_score / self.root.visits])
        return self.root.move

    def select(self):
        node = self.root
        while len(node.children) > 0:
            node = node.get_child_with_best_ucb()
        # print('select:', node)
        return node

    def expand(self, node):
        # print('expand:', node)
        for i, j in get_potential_moves(node.board):
            child = State(clone_board(node.board), opponent(node.player))
            child.board[i][j] = child.player
            child.move = (i, j)
            child.parent = node
            node.children.append(child)

    def simulate(self, node):
        # print('simulate:', node)
        temp_state = node.clone()
        status = check_board_status(temp_state.board)
        if status == opponent(self.player):
            temp_state.parent.win_score = -INF
            return status

        while status == IN_PROGRESS:
            temp_state.random_play()
            status = check_board_status(temp_state.board)
        return status

    def back_propagation(self, node, status):
        temp = node
        while temp is not None:
            temp.visits += 1
            if status == temp.player:
                temp.win_score += WIN_SCORE
            # print('back-propagate:', temp)
            temp = temp.parent
