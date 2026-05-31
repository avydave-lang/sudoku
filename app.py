import streamlit as st
import time
import copy
from generator import generate_puzzle, get_hint
from validator import validate_move, is_complete, count_mistakes

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sudoku",
    page_icon="🔢",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

h1 { font-family: 'Syne', sans-serif; font-weight: 800; letter-spacing: -1px; }

/* Sudoku grid table */
.sudoku-table {
    border-collapse: collapse;
    margin: 0 auto 1.5rem auto;
}
.sudoku-table td {
    width: 44px; height: 44px;
    text-align: center; vertical-align: middle;
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    border: 1px solid #ccc;
    background: #fff;
    color: #1a1a2e;
    padding: 0;
}
.sudoku-table td.given {
    background: #f0f4ff;
    font-weight: 700;
    color: #1a1a2e;
}
.sudoku-table td.wrong {
    color: #e63946;
}
.sudoku-table td.hint-cell {
    background: #d4f7dc;
    color: #2d6a4f;
    font-weight: 700;
}
.sudoku-table td.box-right  { border-right:  2.5px solid #333; }
.sudoku-table td.box-bottom { border-bottom: 2.5px solid #333; }

/* Stat pill */
.stat-pill {
    display: inline-block;
    background: #1a1a2e;
    color: #e2e8f0;
    border-radius: 999px;
    padding: 4px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    margin: 2px 4px;
}

/* Win banner */
.win-banner {
    background: linear-gradient(135deg, #06d6a0, #118ab2);
    color: white;
    border-radius: 12px;
    padding: 1.2rem 2rem;
    text-align: center;
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 1rem;
    letter-spacing: -0.5px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state helpers ─────────────────────────────────────────────────────
def init_state():
    defaults = {
        "puzzle":       None,
        "solution":     None,
        "board":        None,
        "given":        None,   # mask of pre-filled cells
        "n":            9,
        "difficulty":   "Medium",
        "undo_stack":   [],
        "redo_stack":   [],
        "start_time":   None,
        "elapsed":      0,
        "running":      False,
        "mistakes":     0,
        "hint_cell":    None,   # (row, col) last hinted
        "won":          False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def new_game(n, difficulty):
    puzzle, solution = generate_puzzle(n, difficulty)
    board = copy.deepcopy(puzzle)
    given = [[puzzle[r][c] != 0 for c in range(n)] for r in range(n)]
    st.session_state.update(
        puzzle=puzzle, solution=solution, board=board, given=given,
        n=n, difficulty=difficulty,
        undo_stack=[], redo_stack=[],
        start_time=time.time(), elapsed=0, running=True,
        mistakes=0, hint_cell=None, won=False,
    )

def push_undo(board):
    st.session_state.undo_stack.append(copy.deepcopy(board))
    st.session_state.redo_stack.clear()

def undo():
    if st.session_state.undo_stack:
        st.session_state.redo_stack.append(copy.deepcopy(st.session_state.board))
        st.session_state.board = st.session_state.undo_stack.pop()
        st.session_state.hint_cell = None

def redo():
    if st.session_state.redo_stack:
        st.session_state.undo_stack.append(copy.deepcopy(st.session_state.board))
        st.session_state.board = st.session_state.redo_stack.pop()
        st.session_state.hint_cell = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ New Game")
    grid_size   = st.selectbox("Grid size",   [6, 9, 16], index=1)
    difficulty  = st.selectbox("Difficulty",  ["Easy", "Medium", "Hard", "Expert"], index=1)
    if st.button("▶  Start New Game", use_container_width=True):
        new_game(grid_size, difficulty)
        st.rerun()

    st.markdown("---")
    st.markdown("### Controls")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("↩ Undo", use_container_width=True):
            undo(); st.rerun()
    with c2:
        if st.button("↪ Redo", use_container_width=True):
            redo(); st.rerun()

    if st.button("💡 Hint", use_container_width=True):
        h = get_hint(st.session_state.board, st.session_state.solution)
        if h:
            r, c, v = h
            push_undo(st.session_state.board)
            st.session_state.board[r][c] = v
            st.session_state.hint_cell = (r, c)
            st.rerun()

    if st.button("✅ Validate", use_container_width=True):
        n = st.session_state.n
        st.session_state.mistakes = count_mistakes(
            st.session_state.board, st.session_state.solution, n)
        st.rerun()

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("# 🔢 Sudoku")

if st.session_state.board is None:
    st.info("Choose a grid size and difficulty in the sidebar, then press **Start New Game**.")
    st.stop()

# ── Timer ─────────────────────────────────────────────────────────────────────
n = st.session_state.n
if st.session_state.running and not st.session_state.won:
    elapsed = int(time.time() - st.session_state.start_time)
else:
    elapsed = int(st.session_state.elapsed)
mins, secs = divmod(elapsed, 60)
timer_str = f"{mins:02d}:{secs:02d}"

# ── Stats row ─────────────────────────────────────────────────────────────────
st.markdown(
    f'<span class="stat-pill">⏱ {timer_str}</span>'
    f'<span class="stat-pill">🎯 {n}×{n}</span>'
    f'<span class="stat-pill">📊 {st.session_state.difficulty}</span>'
    f'<span class="stat-pill">❌ {st.session_state.mistakes} mistakes</span>',
    unsafe_allow_html=True,
)
st.markdown("")

# ── Win check ─────────────────────────────────────────────────────────────────
if is_complete(st.session_state.board, n):
    if not st.session_state.won:
        st.session_state.won = True
        st.session_state.running = False
        st.session_state.elapsed = time.time() - st.session_state.start_time
    st.markdown(
        f'<div class="win-banner">🎉 Puzzle Solved in {timer_str}!</div>',
        unsafe_allow_html=True,
    )

# ── Build HTML grid ───────────────────────────────────────────────────────────
from generator import get_box_size
br, bc = get_box_size(n)
board    = st.session_state.board
given    = st.session_state.given
solution = st.session_state.solution
hint_cell = st.session_state.hint_cell

def cell_html(r, c):
    val = board[r][c]
    classes = []
    if given[r][c]:
        classes.append("given")
    elif val != 0 and val != solution[r][c]:
        classes.append("wrong")
    if hint_cell and hint_cell == (r, c):
        classes.append("hint-cell")
    # thick borders for box boundaries
    if (c + 1) % bc == 0 and c != n - 1:
        classes.append("box-right")
    if (r + 1) % br == 0 and r != n - 1:
        classes.append("box-bottom")
    cls = " ".join(classes)
    display = str(val) if val != 0 else "&nbsp;"
    return f'<td class="{cls}">{display}</td>'

rows_html = ""
for r in range(n):
    row_html = "".join(cell_html(r, c) for c in range(n))
    rows_html += f"<tr>{row_html}</tr>"

grid_html = f'<table class="sudoku-table">{rows_html}</table>'
st.markdown(grid_html, unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────────
if not st.session_state.won:
    st.markdown("### ✏️ Enter a value")
    col1, col2, col3 = st.columns(3)
    with col1:
        row_in = st.number_input("Row",    min_value=1, max_value=n, step=1, key="row_in")
    with col2:
        col_in = st.number_input("Column", min_value=1, max_value=n, step=1, key="col_in")
    with col3:
        val_in = st.number_input("Value",  min_value=1, max_value=n, step=1, key="val_in")

    sub1, sub2 = st.columns([2, 1])
    with sub1:
        if st.button("Place value", use_container_width=True):
            r, c, v = int(row_in) - 1, int(col_in) - 1, int(val_in)
            if given[r][c]:
                st.warning("That cell is pre-filled — choose an empty cell.")
            else:
                push_undo(board)
                board[r][c] = v
                st.session_state.hint_cell = None
                st.rerun()
    with sub2:
        if st.button("🗑 Clear cell", use_container_width=True):
            r, c = int(row_in) - 1, int(col_in) - 1
            if not given[r][c]:
                push_undo(board)
                board[r][c] = 0
                st.session_state.hint_cell = None
                st.rerun()

# ── Auto-refresh while running ────────────────────────────────────────────────
if st.session_state.running and not st.session_state.won:
    time.sleep(1)
    st.rerun()
