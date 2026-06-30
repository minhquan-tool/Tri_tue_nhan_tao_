AI_MARK = "O"
PLAYER_MARK = "X"
EMPTY_CELL = " "

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # hàng ngang
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # hàng dọc
    (0, 4, 8), (2, 4, 6)              # đường chéo
]


def get_empty_cells(game_board):
    """Trả về danh sách các ô còn trống trên bàn cờ."""
    return [index for index, cell in enumerate(game_board) if cell == EMPTY_CELL]


def check_winner(game_board):
    for first, second, third in WIN_LINES:
        if game_board[first] == game_board[second] == game_board[third] != EMPTY_CELL:
            if game_board[first] == AI_MARK:
                return 10
            return -10

    if len(get_empty_cells(game_board)) == 0:
        return 0

    return None