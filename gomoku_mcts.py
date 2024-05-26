import math
import random
import time

from board_utils import get_empty_positions, clone_board, check_board_status, IN_PROGRESS, get_potential_moves, is_empty
from gomoku_model import GomokuAI

INF = 2 ** 32 - 1
WIN_SCORE = 10  # điểm thưởng cho mỗi giả lập thắng
THINKING_TIME = 2000  # thời gian để tính toán một nước đi


# trả lại đối thủ của player (1-X, 2-O)
def opponent(player):
    return 3 - player


# chỉ số heuristic tính lợi thế của một nước đi
def heuristic(node):
    board = node.board
    opp = node.player
    player = opponent(opp)
    (i0, j0) = node.move
    directions = [[0, 1], [1, 1], [1, 0], [1, -1]]
    h = 0

    for d in directions:
        line_length = 1
        closed = 0
        i, j = i0 - d[0], j0 - d[1]
        try:
            while board[i][j] == player:
                line_length += 1
                i -= d[0]
                j -= d[1]
            if board[i][j] == opp:
                closed += 1
        except IndexError:
            closed += 1

        i, j = i0 + d[0], j0 + d[1]
        try:
            while board[i][j] == player:
                line_length += 1
                i += d[0]
                j += d[1]
            if board[i][j] == opp:
                closed += 1
        except IndexError:
            closed += 1

        # print("line_length =", line_length)
        # print("closed =", closed)

        if line_length == 1:
            continue
        if closed == 0 or line_length >= 5:
            h += line_length * line_length
        elif closed == 1:
            h += (line_length * line_length) >> 2

    # print("heuristic =", h)
    return h


# chỉ số UCB1 phản ánh độ ưu tiên khi khám phá một nút (lớn nếu nút đó có thống kê tốt hoặc chưa được thăm nhiều lần)
def ucb1(node):
    h = heuristic(node)
    # print("1:", INF if node.visits == 0 else node.win_score / node.visits)
    # print("2:", INF if node.visits == 0 else 2 * math.sqrt(math.log(node.parent.visits) / node.visits))
    # print("3:", h)
    res = h if node.visits == 0 else node.win_score / node.visits + 2 * math.sqrt(
        math.log(node.parent.visits) / node.visits) + h / (node.visits + 1)
    # print("res:", res)
    return res


# chỉ số thống kê của một nút (giống như tỷ lệ thắng)
def score(node):
    if node.visits == 0:
        return -INF  # nếu chưa thăm thì không nên chọn
    return node.win_score / node.visits


# lớp đại diện cho một nút trạng thái trong cây tìm kiếm
class State:
    def __init__(self, board, player, move=None, parent=None):
        self.parent = parent  # nút cha
        self.children = []  # các nút con
        self.player = player  # người chơi di chuyển trước đó
        self.move = move  # nước đi dẫn tới trạng thái này
        self.visits = 0  # số lần thăm
        self.win_score = 0  # điểm tích lũy
        self.board = board  # bàn cờ

    # trả về một nút con ngẫu nhiên
    def get_random_child(self):
        if len(self.children) == 0:
            return None
        return random.choice(self.children)

    # trả về nút con có thống kê tốt nhất
    def get_best_child(self):
        return max(self.children, key=score)

    # trả về nút con có chỉ số UCB1 tốt nhất
    def get_child_with_best_ucb(self):
        return max(self.children, key=ucb1)

    # đi một nước ngẫu nhiên để biến đổi thành trạng thái tiếp theo
    def random_play(self):
        self.player = opponent(self.player)
        pos = random.choice(get_potential_moves(self.board))
        self.board[pos[0]][pos[1]] = self.player

    # tạo bản sao để phục vụ việc giả lập không ảnh hưởng đến nút ban đầu
    def clone(self):
        clone = State(self.board, self.player, self.move, self.parent)
        clone.children = [child for child in self.children]
        clone.visits = self.visits
        clone.win_score = self.win_score
        clone.board = clone_board(self.board)
        return clone


# lớp đại diện cho thuật toán MCTS
class GomokuMCTS(GomokuAI):
    def __init__(self, player, thinking_time=5000):
        self.name = "MCTS"
        self.root = None  # nút gốc
        self.player = player  # người chơi mà AI nắm giữ (X hay O)
        global THINKING_TIME  # thời gian tính toán cố định cho mỗi nước đi
        THINKING_TIME = thinking_time
        self.simulation_count = 0  # biến đếm số lần giả lập

    # nhận vào một bàn cờ và tính toán nước đi tiếp theo
    def calculate_move(self, board):
        print('Reset sim count')
        self.simulation_count = 0

        # nếu bàn cờ rỗng thì trả về một nước đi ngẫu nhiên
        if is_empty(board):
            # tùy chọn đánh cách lề một số ô vì đánh gần lề không có ích
            padding = 1
            move = [random.randint(padding, len(board) - 1 - padding),
                    random.randint(padding, len(board[0]) - 1 - padding),
                    0, 0]
            # print(self.player, ':', move)
            return move

        # nếu chưa có nút gốc thì khởi tạo nút gốc
        if self.root is None:
            self.root = State(board, self.player)
        # còn nếu đã có sẵn nút gốc
        else:
            # tìm xem bàn cờ đầu vào có phải một trong những nút con của nút gốc không
            find_result = [b for b in self.root.children if b == board]
            # nếu không thì tạo nút gốc mới
            if len(find_result) == 0:
                self.root = State(board, self.player)
            # nếu có thì lấy luôn nút đó làm nút gốc mới
            else:
                self.root = find_result[0]
                self.root.parent = None

        start_time = time.perf_counter()
        # lặp lại quá trình tính toán cho đến khi hết thời gian chỉ định
        while int(round((time.perf_counter() - start_time) * 1000)) <= THINKING_TIME:
            # chọn ra một nút lá tiềm năng để phát triển
            selected_node = self.select()
            if check_board_status(selected_node.board) == IN_PROGRESS:
                # nếu chưa phải trạng thái cuối thì mở rộng nút đã chọn
                self.expand(selected_node)
            explored_node = selected_node
            if len(selected_node.children) > 0:
                # nếu nút đã chọn có con thì chọn một nút con ngẫu nhiên để khám phá
                explored_node = selected_node.get_random_child()
            # giả lập một ván đấu hoàn thiện từ nút vừa chọn để lấy kết quả
            status = self.simulate(explored_node)
            # cập nhật thống kê của các nút trên đường đi hiện tại dựa trên kết quả đó
            self.back_propagation(explored_node, status)

        # sau khi hết thời gian, chọn ra nút con của nút gốc có thống kê tốt nhất làm nước đi tiếp theo
        best_child = self.root.get_best_child()
        print("1:", INF if best_child.visits == 0 else best_child.win_score / best_child.visits)
        print("2:",
              INF if best_child.visits == 0 else 2 * math.sqrt(math.log(best_child.parent.visits) / best_child.visits))
        print("3:", heuristic(best_child) / (best_child.visits + 1))
        self.root = best_child
        self.root.parent = None
        # print(self.player, ':', [self.root.move[0], self.root.move[1], self.root.win_score / self.root.visits])
        return [*self.root.move, score(self.root), self.simulation_count]

    # chọn ra một nút lá tiềm năng để phát triển
    def select(self):
        node = self.root
        while len(node.children) > 0:
            node = node.get_child_with_best_ucb()
        # print('select:', node)
        return node

    # sinh ra các nút con cho một nút lá
    def expand(self, node):
        # print('expand:', node)
        for i, j in get_potential_moves(node.board):
            child = State(clone_board(node.board), opponent(node.player))
            child.board[i][j] = child.player
            child.move = (i, j)
            child.parent = node
            node.children.append(child)

    # giả lập một ván đấu hoàn chỉnh rồi trả về kết quả
    def simulate(self, node):
        self.simulation_count += 1
        # print('simulate:', node)
        temp_state = node.clone()
        # kiểm tra trạng thái hiện tại
        status = check_board_status(temp_state.board)
        # nếu đối thủ đã thắng thì phạt điểm âm vô cùng
        if status == opponent(self.player):
            temp_state.parent.win_score = -INF
            return status

        # đi từng nước ngẫu nhiên cho đến khi kết thúc
        while status == IN_PROGRESS:
            temp_state.random_play()
            status = check_board_status(temp_state.board)
        return status

    # cập nhật thống kê cho các nút trên nhánh hiện tại dựa trên kết quả giả lập
    def back_propagation(self, node, status):
        temp = node
        while temp is not None:
            temp.visits += 1
            if status == temp.player:
                temp.win_score += WIN_SCORE
            # print('back-propagate:', temp)
            temp = temp.parent
