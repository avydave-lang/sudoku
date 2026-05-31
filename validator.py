from generator import get_box_size


def validate_move(board, row, col, value, n):
    """Returns True if placing value at (row,col) is valid."""
    original = board[row][col]
    board[row][col] = 0  # temporarily clear
    result = _check_valid(board, row, col, value, n)
    board[row][col] = original
    return result


def _check_valid(board, row, col, value, n):
    br, bc = get_box_size(n)
    if value in board[row]:
        return False
    if value in [board[r][col] for r in range(n)]:
        return False
    box_r, box_c = (row // br) * br, (col // bc) * bc
    for r in range(box_r, box_r + br):
        for c in range(box_c, box_c + bc):
            if board[r][c] == value:
                return False
    return True


def is_complete(board, n):
    """Returns True if the board is fully and correctly filled."""
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0:
                return False
            if not _check_valid(board, r, c, board[r][c], n):
                return False
    return True


def count_mistakes(board, solution, n):
    """Count cells that are filled but wrong."""
    mistakes = 0
    for r in range(n):
        for c in range(n):
            if board[r][c] != 0 and board[r][c] != solution[r][c]:
                mistakes += 1
    return mistakes
