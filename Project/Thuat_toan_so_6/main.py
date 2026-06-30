import math
import tkinter as tk
from tkinter import ttk

from Demo.test import AI_MARK, PLAYER_MARK, EMPTY_CELL, check_winner, get_empty_cells
from Demo.minnimax import minimax
from Demo.alphabeta import alpha_beta
from Demo.expectimax import expectimax


ALGORITHM_NAMES = ("Minimax", "Alpha-Beta", "Expectimax")

# ----------------------- BẢNG MÀU (DARK THEME) -----------------------
COLOR_BG = "#1b1f27"            # nền tổng thể
COLOR_PANEL = "#242a35"         # nền panel điều khiển
COLOR_BOARD_BG = "#10131a"      # nền quanh bàn cờ
COLOR_CELL_IDLE = "#2c333f"     # ô trống
COLOR_CELL_HOVER = "#3a4254"    # ô khi hover
COLOR_CELL_WIN = "#2e6f4f"      # ô thuộc đường thắng
COLOR_X = "#5aa9ff"             # màu người chơi X
COLOR_O = "#ff6f6f"             # màu AI O
COLOR_TEXT = "#e8eaf0"
COLOR_SUBTEXT = "#9aa3b2"
COLOR_ACCENT = "#5aa9ff"
COLOR_LOG_BG = "#0d1117"
COLOR_LOG_TEXT = "#7ee787"
FONT_FAMILY = "Segoe UI"
CELL_FONT = ("Consolas", 40, "bold")

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def calculate_move_score(game_board, algorithm_name, node_counter):
    if algorithm_name == "Minimax":
        return minimax(game_board, False, node_counter)

    if algorithm_name == "Alpha-Beta":
        return alpha_beta(game_board, False, -math.inf, math.inf, node_counter)

    if algorithm_name == "Expectimax":
        return expectimax(game_board, False, node_counter)

    raise ValueError(f"Thuật toán không hợp lệ: {algorithm_name}")

def find_best_ai_move(game_board, algorithm_name):
    best_move = None
    best_score = -math.inf
    node_counter = {"nodes": 0}
    for cell_index in get_empty_cells(game_board):
        game_board[cell_index] = AI_MARK
        current_score = calculate_move_score(game_board, algorithm_name, node_counter)
        game_board[cell_index] = EMPTY_CELL

        if current_score > best_score:
            best_score = current_score
            best_move = cell_index

    return best_move, best_score, node_counter["nodes"]


def find_winning_line(game_board):
    for line in WIN_LINES:
        a, b, c = line
        if game_board[a] != EMPTY_CELL and game_board[a] == game_board[b] == game_board[c]:
            return line
    return None


class CaroApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Bàn cờ caro")
        self.window.configure(bg=COLOR_BG)
        self.window.resizable(False, False)

        self.game_board = [EMPTY_CELL] * 9
        self.cell_buttons = []
        self.Demo_choice = tk.StringVar(value="Minimax")
        self.game_active = True

        self._configure_styles()
        self.create_interface()
        self.write_log("Người chơi là X, AI là O.")
        self.write_log("Chọn thuật toán rồi bắt đầu chơi.")
        self.write_log("-" * 35)

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Custom.TCombobox",
            fieldbackground=COLOR_PANEL,
            background=COLOR_PANEL,
            foreground=COLOR_TEXT,
            arrowcolor=COLOR_TEXT,
            padding=6,
        )
        style.map(
            "Custom.TCombobox",
            fieldbackground=[("readonly", COLOR_PANEL)],
            foreground=[("readonly", COLOR_TEXT)],
        )

    # ----------------------------------------------------------------
    def create_interface(self):
        main_frame = tk.Frame(self.window, bg=COLOR_BG, padx=20, pady=20)
        main_frame.pack()

        title_label = tk.Label(
            main_frame,
            text="Quyết đấu cùng AI",
            font=(FONT_FAMILY, 20, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 4), sticky="w")

        subtitle_label = tk.Label(
            main_frame,
            text="Người chơi [Bạn] (X)  vs.  Trí tuệ nhân tạo [AI] (O)",
            font=(FONT_FAMILY, 10),
            fg=COLOR_SUBTEXT,
            bg=COLOR_BG,
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 16), sticky="w")

        # ---------------- BÀN CỜ ----------------
        board_outer = tk.Frame(main_frame, bg=COLOR_BOARD_BG, padx=12, pady=12)
        board_outer.grid(row=2, column=0, padx=(0, 16), sticky="n")

        board_frame = tk.Frame(board_outer, bg=COLOR_BOARD_BG)
        board_frame.pack()

        for cell_index in range(9):
            button = tk.Button(
                board_frame,
                text=EMPTY_CELL,
                font=CELL_FONT,
                width=3,
                height=1,
                bg=COLOR_CELL_IDLE,
                fg=COLOR_TEXT,
                activebackground=COLOR_CELL_HOVER,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda index=cell_index: self.player_move(index),
            )
            button.grid(
                row=cell_index // 3,
                column=cell_index % 3,
                padx=4,
                pady=4,
                ipadx=4,
                ipady=4,
            )
            button.bind("<Enter>", lambda e, b=button: self._on_cell_hover(b, True))
            button.bind("<Leave>", lambda e, b=button: self._on_cell_hover(b, False))
            self.cell_buttons.append(button)

        # ---------------- PANEL ĐIỀU KHIỂN ----------------
        control_frame = tk.Frame(main_frame, bg=COLOR_PANEL, padx=16, pady=16)
        control_frame.grid(row=2, column=1, sticky="n")

        tk.Label(
            control_frame,
            text="THUẬT TOÁN AI",
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLOR_SUBTEXT,
            bg=COLOR_PANEL,
        ).pack(anchor="w")

        algorithm_box = ttk.Combobox(
            control_frame,
            textvariable=self.Demo_choice,
            values=ALGORITHM_NAMES,
            state="readonly",
            style="Custom.TCombobox",
            width=24,
        )
        algorithm_box.pack(pady=(6, 14), fill="x")

        self.status_label = tk.Label(
            control_frame,
            text="Lượt của bạn (X)",
            font=(FONT_FAMILY, 11, "bold"),
            fg=COLOR_X,
            bg=COLOR_PANEL,
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        reset_button = tk.Button(
            control_frame,
            text="↺  Làm mới bàn cờ",
            command=self.reset_game,
            bg=COLOR_ACCENT,
            fg="#0d1117",
            activebackground="#7cbcff",
            font=(FONT_FAMILY, 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=8,
        )
        reset_button.pack(fill="x", pady=(0, 16))

        tk.Label(
            control_frame,
            text="CONSOLE LOG",
            font=(FONT_FAMILY, 10, "bold"),
            fg=COLOR_SUBTEXT,
            bg=COLOR_PANEL,
        ).pack(anchor="w")

        log_container = tk.Frame(control_frame, bg=COLOR_LOG_BG)
        log_container.pack(pady=(6, 0))

        self.log_box = tk.Text(
            log_container,
            height=14,
            width=42,
            state="disabled",
            bg=COLOR_LOG_BG,
            fg=COLOR_LOG_TEXT,
            insertbackground=COLOR_LOG_TEXT,
            font=("Consolas", 9),
            relief="flat",
            bd=8,
            wrap="word",
        )
        self.log_box.pack()

    # ----------------------------------------------------------------
    def _on_cell_hover(self, button, entering):
        if button["state"] == "disabled" or button["text"] != EMPTY_CELL:
            return
        button.config(bg=COLOR_CELL_HOVER if entering else COLOR_CELL_IDLE)

    def write_log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def reset_game(self):
        self.game_board = [EMPTY_CELL] * 9
        self.game_active = True

        for button in self.cell_buttons:
            button.config(text=EMPTY_CELL, state="normal", bg=COLOR_CELL_IDLE, fg=COLOR_TEXT)

        self.status_label.config(text="Lượt của bạn (X)", fg=COLOR_X)
        self.write_log("\n>>> Đã làm mới bàn cờ <<<")

    def player_move(self, cell_index):
        if not self.game_active or self.game_board[cell_index] != EMPTY_CELL:
            return

        self.game_board[cell_index] = PLAYER_MARK
        self.cell_buttons[cell_index].config(text=PLAYER_MARK, fg=COLOR_X)
        self.write_log(f"Người chơi X đánh ô: {cell_index}")

        if self.is_game_finished():
            return

        self.status_label.config(text="AI đang suy nghĩ...", fg=COLOR_O)
        self.window.after(100, self.ai_move)

    def ai_move(self):
        algorithm_name = self.Demo_choice.get()
        self.write_log(f"AI đang chạy thuật toán: {algorithm_name}")
        self.window.update()

        best_move, best_score, total_nodes = find_best_ai_move(self.game_board, algorithm_name)

        if best_move is None:
            return

        self.game_board[best_move] = AI_MARK
        self.cell_buttons[best_move].config(text=AI_MARK, fg=COLOR_O)

        self.write_log(f"AI O đánh ô: {best_move}")
        self.write_log(f"Điểm nước đi: {best_score}")
        self.write_log(f"Số node đã duyệt: {total_nodes}")
        self.write_log("-" * 35)

        if not self.is_game_finished():
            self.status_label.config(text="Lượt của bạn (X)", fg=COLOR_X)

    def is_game_finished(self):
        result_score = check_winner(self.game_board)

        if result_score is None:
            return False

        winning_line = find_winning_line(self.game_board)
        if winning_line:
            for index in winning_line:
                self.cell_buttons[index].config(bg=COLOR_CELL_WIN)

        if result_score == 10:
            self.write_log("KẾT QUẢ: AI THẮNG!")
            self.status_label.config(text=" AI thắng!", fg=COLOR_O)
        elif result_score == -10:
            self.write_log("KẾT QUẢ: BẠN THẮNG!")
            self.status_label.config(text=" Bạn thắng!", fg=COLOR_X)
        else:
            self.write_log("KẾT QUẢ: HÒA!")
            self.status_label.config(text=" Hòa!", fg=COLOR_SUBTEXT)

        self.lock_board()
        return True

    def lock_board(self):
        self.game_active = False
        for button in self.cell_buttons:
            button.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = CaroApp(root)
    root.mainloop()