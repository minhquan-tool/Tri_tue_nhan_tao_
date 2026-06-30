import math
from Demo.test import AI_MARK, PLAYER_MARK, EMPTY_CELL, check_winner, get_empty_cells


def expectimax(game_board, is_ai_turn, node_counter):
    """
    Expectimax:
    - AI chọn nước đi có điểm cao nhất.
    - Người chơi được xem như đi ngẫu nhiên.
    Vì vậy lượt người chơi lấy điểm trung bình của các khả năng.
    """
    node_counter["nodes"] += 1

    result_score = check_winner(game_board)
    if result_score is not None:
        return result_score

    empty_cells = get_empty_cells(game_board)

    if is_ai_turn:
        best_score = -math.inf

        for cell_index in empty_cells:
            game_board[cell_index] = AI_MARK
            current_score = expectimax(game_board, False, node_counter)
            game_board[cell_index] = EMPTY_CELL

            best_score = max(best_score, current_score)

        return best_score

    total_score = 0

    for cell_index in empty_cells:
        game_board[cell_index] = PLAYER_MARK
        current_score = expectimax(game_board, True, node_counter)
        game_board[cell_index] = EMPTY_CELL

        total_score += current_score

    return total_score / len(empty_cells)