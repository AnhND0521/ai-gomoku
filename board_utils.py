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
