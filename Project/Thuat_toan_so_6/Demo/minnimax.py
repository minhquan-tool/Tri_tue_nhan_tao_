import math
from Demo.test import AI_MARK, PLAYER_MARK, EMPTY_CELL, check_winner, get_empty_cells


def minimax(game_board, is_ai_turn, node_counter):
    """
    Minimax:
    - AI chọn nước có điểm cao nhất.
    - Người chơi chọn nước có điểm thấp nhất.
    """
    node_counter["nodes"] += 1

    result_score = check_winner(game_board)
    if result_score is not None:
        return result_score

    if is_ai_turn:
        best_score = -math.inf

        for cell_index in get_empty_cells(game_board):
            game_board[cell_index] = AI_MARK
            current_score = minimax(game_board, False, node_counter)
            game_board[cell_index] = EMPTY_CELL

            best_score = max(best_score, current_score)

        return best_score

    best_score = math.inf

    for cell_index in get_empty_cells(game_board):
        game_board[cell_index] = PLAYER_MARK
        current_score = minimax(game_board, True, node_counter)
        game_board[cell_index] = EMPTY_CELL

        best_score = min(best_score, current_score)

    return best_score