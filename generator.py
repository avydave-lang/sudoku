import random
import copy

# Difficulty: fraction of cells to REMOVE
DIFFICULTY_REMOVE = {
    "Easy":   0.40,
    "Medium": 0.55,
    "Hard":   0.65,
    "Expert": 0.75,
}

def get_box_size(n):
    """Return (rows, cols) of a sub-box for grid size n."""
    if n == 6:
        return (2, 3)
    elif n == 9:
        return (3, 3)
    elif n == 16:
        return (4, 4)
    raise ValueError(f"Unsupported grid size: {n}")


def is_valid(board, row, col, num, n):
    br, bc = get_box_size(n)
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(n)]:
        return False
    box_r, box_c = (row // br) * br, (col // bc) * bc
    for r in range(box_r, box_r + br):
        for c in range(box_c, box_c + bc):
            if board[r][c] == num:
                return False
    return True


def solve(board, n):
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0:
                nums = list(range(1, n + 1))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, r, c, num, n):
                        board[r][c] = num
                        if solve(board, n):
                            return True
                        board[r][c] = 0
                return False
    return True


def generate_puzzle(n=9, difficulty="Medium"):
    """Returns (puzzle, solution) as 2D lists of ints (0 = empty)."""
    board = [[0] * n for _ in range(n)]
    solve(board, n)
    solution = copy.deepcopy(board)

    remove_frac = DIFFICULTY_REMOVE.get(difficulty, 0.55)
    cells = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(cells)
    remove_count = int(n * n * remove_frac)

    puzzle = copy.deepcopy(board)
    for r, c in cells[:remove_count]:
        puzzle[r][c] = 0

    return puzzle, solution


def get_hint(puzzle, solution):
    """Return (row, col, value) for the first empty cell, or None."""
    n = len(puzzle)
    for r in range(n):
        for c in range(n):
            if puzzle[r][c] == 0:
                return (r, c, solution[r][c])
    return None
