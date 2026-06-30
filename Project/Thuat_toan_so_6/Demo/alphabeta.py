import math
from Demo.test import AI_MARK, PLAYER_MARK, EMPTY_CELL, check_winner, get_empty_cells


def alpha_beta(game_board, is_ai_turn, alpha, beta, node_counter):
    """
    Alpha-Beta Pruning:
    Giống Minimax nhưng cắt bỏ các nhánh không cần xét.
    alpha: điểm tốt nhất hiện tại của AI.
    beta : điểm tốt nhất hiện tại của người chơi.
    """
    node_counter["nodes"] += 1

    result_score = check_winner(game_board)
    if result_score is not None:
        return result_score

    if is_ai_turn:
        best_score = -math.inf

        for cell_index in get_empty_cells(game_board):
            game_board[cell_index] = AI_MARK
            current_score = alpha_beta(game_board, False, alpha, beta, node_counter)
            game_board[cell_index] = EMPTY_CELL

            best_score = max(best_score, current_score)
            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score

    best_score = math.inf

    for cell_index in get_empty_cells(game_board):
        game_board[cell_index] = PLAYER_MARK
        current_score = alpha_beta(game_board, True, alpha, beta, node_counter)
        game_board[cell_index] = EMPTY_CELL

        best_score = min(best_score, current_score)
        beta = min(beta, best_score)

        if beta <= alpha:
            break

    return best_score