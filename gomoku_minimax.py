from IPython.display import clear_output
import random, copy

from gomoku_model import GomokuAI

DEEP_MAX = 2  # độ sâu tìm kiếm
WINNING_SCORE = 10 ** 10  # điểm thắng cuộc
SIZE = 15


class GomokuMinimax(GomokuAI):
    def __init__(self, board_size, bot_mark, max_depth=2):
        self.bot_mark = bot_mark
        self.name = 'MINIMAX'
        global SIZE
        SIZE = board_size
        global DEEP_MAX
        DEEP_MAX = max_depth
        print('init minimax player of', ['', 'X', 'O'][bot_mark])

    # hàm này sẽ trả về một list là các nước đi cạnh những ô đã được đánh rồi
    # chẳng hạn như nếu bàn cờ hiện tại chỉ mới có 1 nước được đánh ở giữa bàn cờ
    # thì hàm sẽ trả về list có 8 phần tử là các ô xung quanh
    def generate_move(self, board) -> list:
        possible_moves = []
        imax, jmax = len(board), len(board[0])
        # board = [[board[i][j] for j in range(jmax)] for i in range(imax)]
        # duyệt cả bàn cờ
        for row in range(SIZE):
            for col in range(SIZE):
                # nếu ô hiện tại đã đánh rồi, bỏ qua
                if board[row][col] > 0:
                    continue
                # ngược lại nếu chưa được đánh, ta sẽ kiểm tra các vị trí xung
                # quanh ô này đã được đánh chưa, nếu có thì thêm vào possible_moves
                if row > 0:
                    if col > 0:
                        if board[row - 1][col - 1] > 0 or board[row][col - 1] > 0:
                            possible_moves.append((row, col))
                    if col < SIZE - 1:
                        if board[row - 1][col + 1] > 0 or board[row][col + 1] > 0:
                            possible_moves.append((row, col))
                    if board[row - 1][col] > 0:
                        possible_moves.append((row, col))
                if row < SIZE - 1:
                    if col > 0:
                        if board[row + 1][col - 1] > 0 or board[row][col - 1] > 0:
                            possible_moves.append((row, col))
                    if col < SIZE - 1:
                        if board[row + 1][col + 1] > 0 or board[row][col + 1] > 0:
                            possible_moves.append((row, col))
                    if board[row + 1][col] > 0:
                        possible_moves.append((row, col))
        return possible_moves

    # hàm lấy điểm dựa vào vị trí thế cờ
    def get_score(self, consecutive, blocked_side, is_turn) -> int:
        # bị chặn cả 2 bên mà dưới 5 ô liên tiếp thì là nước cờ chết 
        if blocked_side == 2 and consecutive < 5:
            return 0
        if blocked_side < 0:
            return 0
        if consecutive <= 0:
            return 0

            # 5 ô liên tiếp là thắng
        if consecutive == 5:
            return WINNING_SCORE

            # 4 ô liên tiếp
        if consecutive == 4:
            # hiện tại là lượt đánh của máy -> thắng 
            if is_turn:
                return WINNING_SCORE / 10
                # lượt sau thắng do cả 2 bên không bị chặn
            elif blocked_side == 0:
                return WINNING_SCORE / 100
                # ép đối phương chặn lượt tiếp theo
            else:
                return 200

                # 3 ô liên tiếp
        elif consecutive == 3:
            # không bên nào bị chặn 
            if blocked_side == 0:
                if is_turn:
                    return WINNING_SCORE / 1000
                    # ép đối phương chặn lượt tiếp theo
                else:
                    return 200
                    # bị chặn 1 bên
            else:
                if is_turn:
                    return 10
                else:
                    return 5

                    # 2 ô liên tiếp
        elif consecutive == 2:
            if blocked_side == 0:
                if is_turn:
                    return 7
                else:
                    return 5
            else:
                return 3

                # 1 ô liên tiếp
        elif consecutive == 1:
            return 1

            # trường hợp 5 ô liên tiếp trờ lên
        else:
            return WINNING_SCORE * 10

    # hàm này đánh giá vị trí hiện tại của bàn cờ, phục vụ cho các hàm đánh giá hàng, cột, đường chéo phía dưới
    # eval = [consecutive, blocked_side, score] (số ô cờ liên tiếp, số bên bị chặn, điểm số)
    def evaluate_position(self, board, x, y, is_bot, is_bot_turn, eval, prepos) -> int:
        # lấy giá trị để so sánh
        val = 0
        if is_bot:
            val = self.bot_mark
        else:
            val = 3 - self.bot_mark

        # nếu cùng là người chơi hoặc máy đánh, tăng số ô liên tiếp thêm 1
        if board[x][y] == val:
            eval[0] += 1

        # nếu ô hiện tại trống
        elif board[x][y] == 0:
            if prepos == 0:
                eval[2] += self.get_score(eval[3], eval[4] - 1, is_bot == is_bot_turn)
            elif prepos == val:
                if eval[3] > 0:
                    eval[2] += self.get_score(min(eval[0] + eval[3], 4), eval[4] - 1, is_bot == is_bot_turn)
                    eval[3] = 0
                else:
                    eval[3] = eval[0]
                    eval[4] = eval[1]

            # đặt lại là bên phải bị chặn
            eval[0] = 0
            eval[1] = 1

        # ô hiện tại là ô cờ của đối phương
        else:
            if eval[3] > 0:
                eval[2] += self.get_score(min(eval[0] + eval[3], 4), eval[4], is_bot == is_bot_turn)
            else:
                eval[2] += self.get_score(eval[0], eval[1], is_bot == is_bot_turn)

            eval[0] = 0
            eval[1] = 2
            eval[3] = 0

    # hàm đánh giá điểm dựa theo thế cờ các hàng
    # eval = [consecutive, blocked_side, score] (số ô cờ liên tiếp, số bên bị chặn, điểm số) 
    def evaluate_row(self, board, is_bot, is_bot_turn) -> int:
        eval = [0, 2, 0, 0, 0]
        for row in range(SIZE):
            prepos = 0
            for col in range(SIZE):
                self.evaluate_position(board, row, col, is_bot, is_bot_turn, eval, prepos)
                prepos = board[row][col]
                # sau khi kết thúc một hàng, cần xem là có thể đánh giá được nốt không (trường hợp đầu tiên của hàm evaluate_position)
            if eval[3] > 0:
                eval[2] += self.get_score(min(eval[0] + eval[3], 4), eval[4], is_bot == is_bot_turn)
            elif eval[0] > 0:
                eval[2] += self.get_score(eval[0], eval[1], is_bot == is_bot_turn)
            eval[0] = 0
            eval[1] = 2
            eval[3] = 0
        return eval[2]

    # hàm đánh giá điểm dựa theo thế cờ các cột 
    # eval = [consecutive, blocked_side, score] (số ô cờ liên tiếp, số bên bị chặn, điểm số) 
    def evaluate_col(self, board, is_bot, is_bot_turn) -> int:
        eval = [0, 2, 0, 0, 0]
        for col in range(SIZE):
            prepos = 0
            for row in range(SIZE):
                self.evaluate_position(board, row, col, is_bot, is_bot_turn, eval, prepos)
                prepos = board[row][col]
                # sau khi kết thúc một cột, cần xem là có thể đánh giá được nốt không (trường hợp đầu tiên của hàm evaluate_position)
            if eval[3] > 0:
                eval[2] += self.get_score(min(eval[0] + eval[3], 4), eval[4], is_bot == is_bot_turn)
            elif eval[0] > 0:
                eval[2] += self.get_score(eval[0], eval[1], is_bot == is_bot_turn)
            eval[0] = 0
            eval[1] = 2
            eval[3] = 0
        return eval[2]

    # hàm đánh giá điểm dựa theo thế cờ các đường chéo 
    # eval = [consecutive, blocked_side, score] (số ô cờ liên tiếp, số bên bị chặn, điểm số) 
    def evaluate_diagonal(self, board, is_bot, is_bot_turn) -> int:
        eval = [0, 2, 0, 0, 0]
        for i in range(2 * SIZE - 1):
            start = max(0, i - SIZE + 1)
            end = min(SIZE - 1, i)
            prepos = 0
            for j in range(start, end + 1):
                self.evaluate_position(board, j, j - i, is_bot, is_bot_turn, eval, prepos)
                prepos = board[j][j - i]

                # sau khi kết thúc một đường chéo, cần xem là có thể đánh giá được nốt không (trường hợp đầu tiên của hàm evaluate_position)
            if eval[3] > 0:
                eval[2] += self.get_score(min(eval[0] + eval[3], 4), eval[4], is_bot == is_bot_turn)
            elif eval[0] > 0:
                eval[2] += self.get_score(eval[0], eval[1], is_bot == is_bot_turn)
            eval[0] = 0
            eval[1] = 2
            eval[3] = 0

        for i in range(1 - SIZE, SIZE):
            start = max(0, i)
            end = min(SIZE + i - 1, SIZE - 1)
            prepos = 0
            for j in range(start, end + 1):
                self.evaluate_position(board, j, i - j, is_bot, is_bot_turn, eval, prepos)
                prepos = board[j][i - j]

                # sau khi kết thúc một đường chéo, cần xem là có thể đánh giá được nốt không (trường hợp đầu tiên của hàm evaluate_position)
            if eval[3] > 0:
                eval[2] += self.get_score(min(eval[0] + eval[3], 4), eval[4], is_bot == is_bot_turn)
            elif eval[0] > 0:
                eval[2] += self.get_score(eval[0], eval[1], is_bot == is_bot_turn)
            eval[0] = 0
            eval[1] = 2
            eval[3] = 0

        return eval[2]

    # hàm trả về điểm số của bàn cờ dựa theo thế cờ các hàng, cột, đường chéo
    def get_board_score(self, board, is_bot, is_bot_turn) -> int:
        return self.evaluate_row(board, is_bot, is_bot_turn) + self.evaluate_col(board, is_bot,
                                                                                 is_bot_turn) + self.evaluate_diagonal(
            board, is_bot, is_bot_turn)

    # hảm trả về điểm số của máy so với người chơi 
    # trả về list để đồng bộ dữ liệu với hàm minimax 
    def get_relative_score(self, board, is_bot_turn) -> list:
        o_score = self.get_board_score(board, True, is_bot_turn)
        x_score = self.get_board_score(board, False, is_bot_turn)
        if x_score == 0:
            x_score = 1
        return [0, 0, o_score / x_score]

    # hàm này tìm xem có nước nào đánh thắng game không, phục vụ cho việc tìm nước đi của máy tốt hơn 
    def search_winning_move(self, board, is_bot) -> tuple:
        moves = self.generate_move(board)
        val = 0
        if is_bot:
            val = self.bot_mark
        else:
            val = 3 - self.bot_mark
        for (x, y) in moves:
            board[x][y] = val
            score = self.get_board_score(board, is_bot, is_bot)
            board[x][y] = 0
            if score >= WINNING_SCORE:
                temp = self.get_relative_score(board, is_bot)
                temp[0] = x
                temp[1] = y
                return temp
        return 0

    # hàm tìm kiếm minimax kết hợp cắt tỉa alpha-beta 
    def minimax(self, board, deep, is_bot, alpha, beta):
        # đã đủ độ sâu, trả về điểm tương quan bàn cờ hiện tại 
        if deep == DEEP_MAX:
            score = self.get_relative_score(board, is_bot)
            return score

        best_move = self.search_winning_move(board, is_bot)
        if best_move != 0:
            return best_move

            # lấy các nước đi hợp lệ
        possible_moves = self.generate_move(board)

        # trường hợp không còn nước đi nào thì chỉ cần trả về điểm là được 
        if len(possible_moves) == 0:
            score = self.get_relative_score(board, is_bot)
            return score

            # bắt đầu quá trình tìm kiếm minimax, khởi tạo nước đi tốt nhất
        best_move = [0, 0, 0]
        # tìm kiếm max - máy 
        if is_bot:
            # khởi tạo điểm số âm vô cùng 
            best_move[2] = -1
            for (x, y) in possible_moves:
                board[x][y] = self.bot_mark
                temp_move = self.minimax(board, deep + 1, False, alpha, beta)
                board[x][y] = 0

                # đổi giá trị alpha 
                if temp_move[2] > alpha:
                    alpha = temp_move[2]

                    # cắt tỉa
                if temp_move[2] >= beta:
                    return temp_move

                if temp_move[2] > best_move[2]:
                    best_move[0] = x
                    best_move[1] = y
                    best_move[2] = temp_move[2]
                    # tìm kiếm min - người chơi
        else:
            # khởi tạo điểm số dương vô cùng 
            best_move[2] = 10 ** 10
            for (x, y) in possible_moves:
                board[x][y] = 3 - self.bot_mark
                temp_move = self.minimax(board, deep + 1, True, alpha, beta)
                board[x][y] = 0

                # đổi giá trị beta 
                if temp_move[2] < beta:
                    beta = temp_move[2]

                    # cắt tỉa
                if temp_move[2] <= alpha:
                    return temp_move

                if temp_move[2] < best_move[2]:
                    best_move[0] = x
                    best_move[1] = y
                    best_move[2] = temp_move[2]

        return best_move

    # hàm tính nước đi cho máy 
    def calculate_move(self, board) -> tuple:
        # nếu bàn cờ rỗng thì trả về nước ngẫu nhiên
        if sum([sum(row) for row in board]) == 0:
            padding = 1
            move = [random.randint(padding, len(board) - 1 - padding),
                    random.randint(padding, len(board[0]) - 1 - padding),
                    0]
            print(self.bot_mark, ':', move)
            return move

        # trước tiên tìm nước đi mà có thể thắng được luôn 
        move = self.search_winning_move(board, True)
        # nếu có thì trả về
        if move != 0:
            print(self.bot_mark, ':', move)
            return move
        # nếu không thì thực hiện tìm kiếm minimax
        else:
            move = self.minimax(board, 0, True, -1, WINNING_SCORE)
            if move != 0:
                print(self.bot_mark, ':', move)
                return move
        return 0

    # hàm in bàn cờ 
    def print_board(self, board):
        print('  ', end='')
        for i in range(SIZE):
            print((i + 1) % 10, end=' ')
        print(*['', ' '], sep='\n', end='')
        print((2 * SIZE + 1) * "-")
        for i in range(SIZE):
            print(*[(i + 1) % 10, "|"], sep='', end='')
            for j in range(SIZE):
                if board[i][j] == 0:
                    print(" ", end='|')
                elif board[i][j] == 1:
                    print("X", end='|')
                else:
                    print("O", end='|')
            print(*['', ' '], sep='\n', end='')
            print((2 * SIZE + 1) * "-")
        print()

    def run(self):
        # khởi tạo một số dữ liệu
        # board[x][y] == 1 nếu là người chơi, == 2 nếu là máy
        board = [[0 for i in range(SIZE)] for j in range(SIZE)]
        game_complete = False
        player_turn = True
        cur_score = 0

        # bắt đầu game
        # nhập lệnh theo cú pháp "mark x y" để đánh một nước
        # chẳng hạn: mark 1 1
        while True:
            # lượt người chơi
            if player_turn:
                command = input().split()
                if command[0] == "exit":
                    clear_output()
                    print("exited!")
                    break
                if len(command) != 3:
                    print("Sai lệnh!")
                    continue
                if command[0] != "mark":
                    print("Sai lệnh!")
                    continue
                try:
                    x = int(command[1])
                    y = int(command[2])
                except:
                    print("Sai lệnh!")
                    continue
                if x < 1 or x > SIZE or y < 1 or y > SIZE:
                    print("Vị trí ngoài phạm vi, hãy thử lại!")
                    continue
                if board[x - 1][y - 1] != 0:
                    print("Ô này đã được đánh, hãy thử ô khác!")
                    continue

                board[x - 1][y - 1] = 1
                player_turn = False

                # xem đã có thế cờ thắng trận chưa
                cur_score = self.get_board_score(board, False, True)
                if cur_score >= WINNING_SCORE:
                    game_complete = True

                    # lượt máy
            else:
                move = self.calculate_move(board)
                board[move[0]][move[1]] = 2
                self.print_board(board)
                player_turn = True

                # xem đã có thế cờ thắng trận chưa
                cur_score = self.get_board_score(board, True, False)
                if cur_score >= WINNING_SCORE:
                    game_complete = True

                    # hiện thị mới bàn cờ
            if player_turn == False:
                clear_output()
                self.print_board(board)

                # xem đã hết game chưa
            if game_complete:
                if player_turn:
                    print("Bot win!")
                    break
                else:
                    print("Player win!")
                    break
