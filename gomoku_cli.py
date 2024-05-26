import time
import matplotlib.pyplot as plt

from board_utils import check_board_status, IN_PROGRESS
from gomoku_mcts import GomokuMCTS
from gomoku_minimax import GomokuMinimax
from gomoku_model import GomokuAI

X, O = 1, 2


def print_board(board):
    print('  ', end='')
    for j in range(len(board[0])):
        print('%2d' % j, end=' ')
    print()

    for i in range(len(board)):
        print('%2d' % i, end=' ')
        for j in range(len(board[i])):
            print(['.', 'X', 'O'][board[i][j]], end='  ')
        print()
    print('-' * 60)


def get_human_move():
    move = map(int, input("Enter move in format of r,c: ").split(',', 1))
    return move


def run_game(board_size=15, bot_x=None, bot_o=None):
    move_count = 0
    minimax_calculating_time = []
    minimax_scores = []
    mcts_simulation_counts = []
    mcts_scores = []

    board = [[0 for j in range(board_size)] for i in range(board_size)]
    players = {
        X: bot_x,
        O: bot_o
    }
    turn = X
    is_minimax_self_play = isinstance(players[X], GomokuMinimax) and isinstance(players[O], GomokuMinimax)
    is_mcts_self_play = isinstance(players[X], GomokuMCTS) and isinstance(players[O], GomokuMCTS)

    while True:
        if isinstance(players[turn], GomokuAI):
            start_time = time.perf_counter()
            move = players[turn].calculate_move(board)
            end_time = time.perf_counter()
            print('Bot move:', move)
            if is_minimax_self_play:
                minimax_calculating_time.append((end_time - start_time))
                minimax_scores.append(move[2])
            if is_mcts_self_play:
                mcts_simulation_counts.append(move[3])
                mcts_scores.append(move[2])

        else:
            move = get_human_move()
        board[move[0]][move[1]] = turn
        move_count += 1
        print_board(board)

        status = check_board_status(board)
        if status != IN_PROGRESS:
            break
        turn = 3 - turn

    print('Result:', ['Draw', 'X wins', 'O wins'][status])

    if is_minimax_self_play:
        plt.title('Thời gian tính toán các nước đi')
        plt.xlabel('Số thứ tự nước đi')
        plt.ylabel('Thời gian (giây)')
        plt.plot(range(1, move_count + 1), minimax_calculating_time)
        plt.show()

        # plt.title('Điểm đánh giá của các nước đi được chọn')
        # plt.xlabel('Số thứ tự nước đi')
        # plt.ylabel('Điểm')
        # plt.plot(range(1, move_count+1), minimax_scores)
        # plt.show()

    if is_mcts_self_play:
        print(move_count)
        print(mcts_simulation_counts)
        plt.title('Số giả lập trước khi đưa ra quyết định')
        plt.xlabel('Số thứ tự nước đi')
        plt.ylabel('Số giả lập')
        plt.ylim(0, 1500)
        plt.plot(range(1, move_count + 1), mcts_simulation_counts)
        plt.show()

        # plt.title('Điểm đánh giá của các nước đi được chọn')
        # plt.xlabel('Số thứ tự nước đi')
        # plt.ylabel('Điểm')
        # plt.plot(range(1, move_count + 1), mcts_scores)
        # plt.show()


if __name__ == '__main__':
    board_size = 15
    # max_depth = 3
    # run_game(board_size,
    #          GomokuMinimax(board_size, X, max_depth=max_depth),
    #          GomokuMinimax(board_size, O, max_depth=max_depth))
    thinking_time = 5000
    run_game(board_size,
             GomokuMCTS(X, thinking_time=thinking_time),
             GomokuMCTS(O, thinking_time=thinking_time))
