import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from board_utils import check_board_status
from gomoku_minimax import GomokuMinimax

X, O = 1, 2


class Mark(QWidget):
    def __init__(self, mark_type, mark_width, parent=None):
        super().__init__()

        self.resize(mark_width, mark_width)

        self.MARK_TYPE = mark_type
        self.MARK_WIDTH = mark_width
        self.setParent(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.MARK_TYPE == X:
            pen = QPen()
            pen.setColor(QColor('red'))
            pen.setWidth(int(0.2 * self.MARK_WIDTH))

            painter.setPen(pen)
            painter.drawLine(0, 0, self.MARK_WIDTH, self.MARK_WIDTH)
            painter.drawLine(0, self.MARK_WIDTH, self.MARK_WIDTH, 0)
        elif self.MARK_TYPE == O:
            pen = QPen()
            pen.setColor(QColor('blue'))
            pen.setWidth(int(0.2 * self.MARK_WIDTH))

            half_pen_width = pen.width() // 2
            painter.setPen(pen)
            painter.drawArc(half_pen_width, half_pen_width, self.MARK_WIDTH - 2 * half_pen_width,
                            self.MARK_WIDTH - 2 * half_pen_width, 0, 360 * 16)

        painter.end()


class GameBoard(QWidget):
    def __init__(self, board_size, player_x=None, player_o=None):
        super().__init__()

        self.setWindowTitle("Gomoku")
        self.resize(1000, 1000)

        self.BOARD_SIZE = board_size
        self.FULL_WIDTH = 1000
        self.MARGIN = 20
        self.CELL_WIDTH = (self.FULL_WIDTH - 2 * self.MARGIN) // board_size
        self.LINE_WIDTH = int(0.05 * self.CELL_WIDTH)
        self.LINE_COLOR = QColor(0, 0, 0)

        self.board = [[0 for i in range(board_size)] for j in range(board_size)]
        self.marks = [[None for i in range(board_size)] for j in range(board_size)]
        self.game_complete = False
        self.turn = X
        self.players = {
            X: player_x,
            O: player_o
        }
        if isinstance(self.players[X], GomokuMinimax):
            self.bot_move()

    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen()
        pen.setWidth(self.LINE_WIDTH)
        pen.setColor(self.LINE_COLOR)
        painter.setPen(pen)

        for i in range(self.BOARD_SIZE + 1):
            offset = self.MARGIN + i * self.CELL_WIDTH
            painter.drawLine(offset, self.MARGIN, offset, self.FULL_WIDTH - self.MARGIN)
            painter.drawLine(self.MARGIN, offset, self.FULL_WIDTH - self.MARGIN, offset)

        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] > 0 and self.marks[i][j] is None:
                    self.draw_mark(i, j, self.board[i][j])

        painter.end()

    def mousePressEvent(self, event):
        if self.game_complete:
            return

        mouse_x, mouse_y = event.pos().x(), event.pos().y()
        if mouse_x < self.MARGIN or mouse_x > self.FULL_WIDTH - self.MARGIN \
                or mouse_y < self.MARGIN or mouse_y > self.FULL_WIDTH - self.MARGIN:
            return

        (i, j) = self.convert_pos_to_index(mouse_x, mouse_y)
        if self.board[i][j] > 0:
            return

        self.board[i][j] = self.turn
        self.turn = 3 - self.turn
        self.repaint()
        if check_board_status(self.board) >= 0:
            self.game_complete = True
            return
        if isinstance(self.players[self.turn], GomokuMinimax):
            self.bot_move()

    def bot_move(self):
        move = self.players[self.turn].calculate_move(self.board)
        self.board[move[0]][move[1]] = self.turn
        self.turn = 3 - self.turn
        self.repaint()
        if check_board_status(self.board) >= 0:
            self.game_complete = True
            return
        if isinstance(self.players[self.turn], GomokuMinimax):
            self.bot_move()

    def draw_mark(self, i, j, mark_type=None):
        mark_width = int(0.8 * self.CELL_WIDTH)
        if mark_type == X or (not mark_type and self.turn == X):
            mark = Mark(X, mark_width, self)
        else:
            mark = Mark(O, mark_width, self)

        (x, y) = self.convert_index_to_pos(i, j)
        offset = (self.CELL_WIDTH - mark_width) // 2
        mark.setGeometry(x + offset, y + offset, mark_width, mark_width)
        mark.show()

    def convert_index_to_pos(self, i, j) -> tuple:
        return (j * self.CELL_WIDTH + self.MARGIN,
                i * self.CELL_WIDTH + self.MARGIN)

    def convert_pos_to_index(self, x, y) -> tuple:
        return ((y - self.MARGIN) // self.CELL_WIDTH,
                (x - self.MARGIN) // self.CELL_WIDTH)


class Game(QMainWindow):
    def __init__(self):
        super().__init__()
        game_board = GameBoard(15, GomokuMinimax(15, X), None)
        hbox = QHBoxLayout(game_board)
        self.resize(1000, 1000)
        self.setLayout(hbox)
        self.setCentralWidget(game_board)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec_())
