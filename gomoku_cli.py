import time
import matplotlib.pyplot as plt

from board_utils import check_board_status, IN_PROGRESS
from gomoku_mcts import GomokuMCTS
from gomoku_minimax import GomokuMinimax
from gomoku_model import GomokuAI

X, O = 1, 2


# Hàm để in ra bàn cờ dưới định dạng dễ quan sát
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
    print()


# Hàm để lấy input từ tác tử con người nếu cần
def get_human_move():
    move = map(int, input("Enter move in format of <row>,<col>: ").split(',', 1))
    return move


# Hàm để chạy một ván đấu với kích cỡ bàn cờ và các người chơi cho trước
def run_game(board_size=15, player_x=None, player_o=None, logging=True):
    move_count = 0
    total_time = {
        X: 0,
        O: 0
    }

    # khởi tạo bàn cờ, người chơi và lượt chơi
    board = [[0 for j in range(board_size)] for i in range(board_size)]
    players = {
        X: player_x,
        O: player_o
    }
    turn = X

    while True:
        if isinstance(players[turn], GomokuAI):
            start_time = time.perf_counter()
            move = players[turn].calculate_move(board)
            end_time = time.perf_counter()
            if logging:
                print('Bot move:', move)
            total_time[turn] += end_time - start_time

        else:
            start_time = time.perf_counter()
            move = get_human_move()
            end_time = time.perf_counter()
            total_time[turn] += end_time - start_time
        board[move[0]][move[1]] = turn
        move_count += 1
        if logging:
            print_board(board)

        status = check_board_status(board)
        if status != IN_PROGRESS:
            break
        turn = 3 - turn

    print('Last state:')
    print_board(board)
    print('Result:', ['Draw', 'X wins', 'O wins'][status])

    x_avg_time = total_time[X] / ((move_count + 1) // 2)
    o_avg_time = total_time[O] / (move_count // 2)

    # trả về kết quả ván đấu và các chỉ số thống kê: số nước đi, thời gian tính nước đi trung bình của X và O
    return [status, move_count, x_avg_time, o_avg_time]


# Hàm đánh giá với tham số là số ván đấu, kích cỡ bàn cờ và hai người chơi X, O
# thực hiện một số
def evaluate(num_games, board_size, player_x, player_o):
    move_counts = []
    x_avg_times = []
    o_avg_times = []
    results = [0, 0, 0]

    for i in range(num_games):
        print('-' * 60)
        print(f'Game {i + 1}/{num_games}')
        status, move_count, x_avg_time, o_avg_time = run_game(board_size, player_x, player_o, logging=False)
        results[status] += 1
        move_counts.append(move_count)
        x_avg_times.append(x_avg_time)
        o_avg_times.append(o_avg_time)
        print('-' * 60)

    print('Kết quả')
    print('X thắng:', results[X])
    print('O thắng:', results[O])
    print('Hòa:', results[0])

    plt.title('Số nước đi mỗi ván')
    plt.xlabel('Ván')
    plt.ylabel('Số nước đi')
    plt.plot(range(1, num_games + 1), move_counts)
    plt.show()

    plt.title('Thời gian tính nước đi trung bình của mỗi người chơi')
    plt.xlabel('Ván')
    plt.ylabel('Thời gian (s)')
    plt.plot(range(1, num_games + 1), x_avg_times, label='X', color='red')
    plt.plot(range(1, num_games + 1), o_avg_times, label='O', color='blue')
    plt.show()


if __name__ == '__main__':
    evaluate(num_games=10, board_size=10, player_x=GomokuMinimax(10, X, 2), player_o=GomokuMCTS(O, 1000))
