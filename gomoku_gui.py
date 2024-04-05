import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QMutex, QSemaphore
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

from board_utils import check_board_status
from gomoku_minimax import GomokuMinimax
from gomoku_model import Human, GomokuAI

X, O = 1, 2
symbols = {
    X: 'X',
    O: 'O'
}


# semaphore = QSemaphore(1)


class Worker(QObject):
    # Define a signal to emit data or status
    move_generated = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(self, game_board):
        super().__init__()
        self.game_board = game_board

    def run(self):
        gb = self.game_board
        while not gb.game_complete and isinstance(gb.players[gb.turn], GomokuAI):
            move = gb.generate_bot_move()
            # semaphore.acquire()
            gb.board[move[0]][move[1]] = gb.turn
            # semaphore.release()
            self.move_generated.emit((move[0], move[1], gb.turn))
            status = check_board_status(gb.board)
            gb.toggle_turn()
        self.finished.emit()


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
    def __init__(self, board_size, player_x=None, player_o=None, game=None):
        super().__init__()

        self.game = game
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
            X: player_x if player_x is not None else Human(),
            O: player_o if player_o is not None else Human()
        }
        if self.players[X].name == self.players[O].name:
            self.players[X].name += '_1'
            self.players[O].name += '_2'

        self.thread = None
        self.worker = None

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

        if isinstance(self.players[self.turn], GomokuAI):
            return

        mouse_x, mouse_y = event.pos().x(), event.pos().y()
        if mouse_x < self.MARGIN or mouse_x > self.FULL_WIDTH - self.MARGIN \
                or mouse_y < self.MARGIN or mouse_y > self.FULL_WIDTH - self.MARGIN:
            return

        (i, j) = self.convert_pos_to_index(mouse_x, mouse_y)
        if self.board[i][j] > 0:
            return

        self.board[i][j] = self.turn
        self.repaint()
        self.toggle_turn()
        if isinstance(self.players[self.turn], GomokuAI):
            self.handle_bot()

    def handle_bot(self):
        self.thread = QThread()
        self.worker = Worker(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.move_generated.connect(self.handle_bot_move)
        self.thread.start()

    def generate_bot_move(self):
        imax, jmax = len(self.board), len(self.board[0])
        board = [[self.board[i][j] for j in range(jmax)] for i in range(imax)]
        return self.players[self.turn].calculate_move(board)

    def handle_bot_move(self, move):
        # semaphore.acquire()
        self.repaint()
        # semaphore.release()

    def draw_mark(self, i, j, mark_type):
        mark_width = int(0.8 * self.CELL_WIDTH)
        if mark_type == X:
            mark = Mark(X, mark_width, self)
        else:
            mark = Mark(O, mark_width, self)

        self.marks[i][j] = mark
        (x, y) = self.convert_index_to_pos(i, j)
        offset = (self.CELL_WIDTH - mark_width) // 2
        mark.setGeometry(x + offset, y + offset, mark_width, mark_width)
        mark.show()

    def toggle_turn(self):
        status = check_board_status(self.board)
        if status >= 0:
            self.game_complete = True
            self.turn = 0
            self.game.prompt.setText('TIE GAME' if status == 0 else f'{symbols[status]} WINS!')
            return
        self.turn = 3 - self.turn
        self.game.prompt.setText(f'{symbols[self.turn]} GOES NEXT')
        self.game.prompt.setStyleSheet(f"color: {'red' if self.turn == X else 'blue'}")

    def convert_index_to_pos(self, i, j) -> tuple:
        return (j * self.CELL_WIDTH + self.MARGIN,
                i * self.CELL_WIDTH + self.MARGIN)

    def convert_pos_to_index(self, x, y) -> tuple:
        return ((y - self.MARGIN) // self.CELL_WIDTH,
                (x - self.MARGIN) // self.CELL_WIDTH)


FONT_FAMILY = 'Segoe UI'


class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.game_board = GameBoard(15, GomokuMinimax(15, X), GomokuMinimax(15, O), self)
        self.prompt = None
        self.player_labels = None
        self.setWindowTitle('Gomoku')
        self.resize(1366, 1040)
        self.setLayout(QHBoxLayout())
        self.set_up_main_panel()
        self.set_up_side_bar()
        self.show()
        if isinstance(self.game_board.players[X], GomokuAI):
            self.game_board.handle_bot()

    def set_up_main_panel(self):
        self.layout().addWidget(self.game_board)

    def set_up_side_bar(self):
        side_bar = QWidget()
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        vbox.setSpacing(40)
        side_bar.setLayout(vbox)
        side_bar.setMaximumWidth(300)

        self.prompt = QLabel('X GOES FIRST')
        self.prompt.setFont(QFont(FONT_FAMILY, 16))
        self.prompt.setAlignment(Qt.AlignHCenter)
        vbox.addWidget(self.prompt)

        new_game_button = QPushButton('New Game')
        new_game_button.setMaximumWidth(200)
        new_game_button.setMinimumWidth(200)
        new_game_button.setFont(QFont(FONT_FAMILY, 14))
        new_game_button.clicked.connect(self.new_game)
        vbox.addWidget(new_game_button)

        quit_button = QPushButton('Quit')
        quit_button.setMaximumWidth(200)
        quit_button.setMinimumWidth(200)
        quit_button.setFont(QFont(FONT_FAMILY, 14))
        quit_button.clicked.connect(self.quit)
        vbox.addWidget(quit_button)

        players_title = QLabel('PLAYERS')
        players_title.setFont(QFont(FONT_FAMILY, 16))
        players_title.setAlignment(Qt.AlignHCenter)
        vbox.addWidget(players_title)

        self.player_labels = {
            X: QLabel(),
            O: QLabel()
        }
        for player in (X, O):
            self.player_labels[player].setText(f'{symbols[player]} - {self.game_board.players[player].name}')
            self.player_labels[player].setAlignment(Qt.AlignLeft)
            self.player_labels[player].setFont(QFont(FONT_FAMILY, 12))
            # self.player_labels[player].setStyleSheet(f"color: {'red' if player == X else 'blue'}")
            vbox.addWidget(self.player_labels[player])

        self.layout().addWidget(side_bar)

    def new_game(self):
        game_board = GameBoard(15, GomokuMinimax(15, X), None, self)
        if isinstance(game_board.players[X], GomokuAI):
            game_board.handle_bot()
        if self.game_board:
            self.game_board.close()
        self.layout().replaceWidget(self.game_board, game_board)
        self.game_board = game_board

    def quit(self):
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec_())
