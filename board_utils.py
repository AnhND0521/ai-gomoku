CONSECUTIVE_MARKS_TO_WIN = 5
IN_PROGRESS = -1
DRAW = 0


def check_board_status(board):
    has_empty_square = False
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] > 0:
                directions = [(0, 1), (1, 1), (1, 0), (1, -1)]
                for d in directions:
                    i_, j_ = i, j
                    consecutive = 0
                    while 0 <= i_ < len(board) and 0 <= j_ < len(board[0]) and board[i_][j_] == board[i][j]:
                        consecutive += 1
                        i_ += d[0]
                        j_ += d[1]
                    if consecutive >= CONSECUTIVE_MARKS_TO_WIN:
                        return board[i][j]
            else:
                has_empty_square = True
    return IN_PROGRESS if has_empty_square else DRAW


def is_empty(board):
    return sum([sum(row) for row in board]) == 0


def get_empty_positions(board):
    return [(i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] == 0]


def get_potential_moves(board):
    possible_moves = []
    # duyệt cả bàn cờ
    for row in range(len(board)):
        for col in range(len(board[row])):
            # nếu ô hiện tại đã đánh rồi, bỏ qua
            if board[row][col] > 0:
                continue
            # ngược lại nếu chưa được đánh, ta sẽ kiểm tra các vị trí xung
            # quanh ô này đã được đánh chưa, nếu có thì thêm vào possible_moves
            if row > 0:
                if col > 0:
                    if board[row - 1][col - 1] > 0 or board[row][col - 1] > 0:
                        possible_moves.append((row, col))
                if col < len(board[row]) - 1:
                    if board[row - 1][col + 1] > 0 or board[row][col + 1] > 0:
                        possible_moves.append((row, col))
                if board[row - 1][col] > 0:
                    possible_moves.append((row, col))
            if row < len(board) - 1:
                if col > 0:
                    if board[row + 1][col - 1] > 0 or board[row][col - 1] > 0:
                        possible_moves.append((row, col))
                if col < len(board[row]) - 1:
                    if board[row + 1][col + 1] > 0 or board[row][col + 1] > 0:
                        possible_moves.append((row, col))
                if board[row + 1][col] > 0:
                    possible_moves.append((row, col))
    return possible_moves


def clone_board(board):
    return [[board[i][j] for j in range(len(board[i]))] for i in range(len(board))]
