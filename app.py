import streamlit as st
import streamlit.components.v1 as components
import time
import copy
import json
from generator import generate_puzzle, get_hint, get_box_size
from validator import is_complete, count_mistakes

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sudoku", page_icon="🔢", layout="centered")

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "puzzle": None, "solution": None, "board": None, "given": None,
        "n": 9, "difficulty": "Medium",
        "undo_stack": [], "redo_stack": [],
        "start_time": None, "elapsed": 0, "running": False,
        "won": False, "hint_cell": None,
        "last_move": None,   # injected by component → {"r","c","v"}
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
        won=False, hint_cell=None, last_move=None,
    )

def push_undo():
    st.session_state.undo_stack.append(copy.deepcopy(st.session_state.board))
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
    grid_size  = st.selectbox("Grid size",  [6, 9, 16], index=1)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Expert"], index=1)
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
            push_undo()
            st.session_state.board[r][c] = v
            st.session_state.hint_cell = (r, c)
            st.rerun()

    if st.button("✅ Validate", use_container_width=True):
        st.session_state.mistakes = count_mistakes(
            st.session_state.board, st.session_state.solution, st.session_state.n)
        st.rerun()

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("# 🔢 Sudoku")

if st.session_state.board is None:
    st.info("Choose a grid size and difficulty in the sidebar, then press **Start New Game**.")
    st.stop()

# ── Apply any move sent from the JS component ─────────────────────────────────
move = st.session_state.get("last_move")
if move and isinstance(move, dict):
    r, c, v = move["r"], move["c"], move["v"]
    n = st.session_state.n
    given = st.session_state.given
    if not given[r][c]:
        push_undo()
        st.session_state.board[r][c] = v
        st.session_state.hint_cell = None
    st.session_state.last_move = None

# ── Timer ─────────────────────────────────────────────────────────────────────
n = st.session_state.n
if st.session_state.running and not st.session_state.won:
    elapsed = int(time.time() - st.session_state.start_time)
else:
    elapsed = int(st.session_state.elapsed)
mins, secs = divmod(elapsed, 60)
timer_str = f"{mins:02d}:{secs:02d}"

# ── Win check ─────────────────────────────────────────────────────────────────
if is_complete(st.session_state.board, n):
    if not st.session_state.won:
        st.session_state.won = True
        st.session_state.running = False
        st.session_state.elapsed = time.time() - st.session_state.start_time

# ── Stats ─────────────────────────────────────────────────────────────────────
mistakes = st.session_state.get("mistakes", 0)
st.markdown(
    f'<style>@import url("https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap");</style>'
    f'<div style="font-family:Space Mono,monospace;margin-bottom:12px">'
    f'<span style="background:#1a1a2e;color:#e2e8f0;border-radius:999px;padding:4px 14px;margin:2px 4px;font-size:.85rem">⏱ {timer_str}</span>'
    f'<span style="background:#1a1a2e;color:#e2e8f0;border-radius:999px;padding:4px 14px;margin:2px 4px;font-size:.85rem">🎯 {n}×{n}</span>'
    f'<span style="background:#1a1a2e;color:#e2e8f0;border-radius:999px;padding:4px 14px;margin:2px 4px;font-size:.85rem">📊 {st.session_state.difficulty}</span>'
    f'<span style="background:#1a1a2e;color:#e2e8f0;border-radius:999px;padding:4px 14px;margin:2px 4px;font-size:.85rem">❌ {mistakes} mistakes</span>'
    f'</div>',
    unsafe_allow_html=True,
)

if st.session_state.won:
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#06d6a0,#118ab2);color:white;border-radius:12px;'
        f'padding:1.2rem 2rem;text-align:center;font-size:1.4rem;font-weight:800;margin-bottom:1rem;'
        f'font-family:Syne,sans-serif">🎉 Puzzle Solved in {timer_str}!</div>',
        unsafe_allow_html=True,
    )

# ── Build interactive HTML/JS grid ────────────────────────────────────────────
br, bc = get_box_size(n)
board    = st.session_state.board
given    = st.session_state.given
solution = st.session_state.solution
hint_cell = st.session_state.hint_cell

# Serialise board state for JS
board_json   = json.dumps(board)
given_json   = json.dumps(given)
solution_json = json.dumps(solution)
hint_json    = json.dumps(list(hint_cell) if hint_cell else None)
won_json     = json.dumps(st.session_state.won)

cell_size = 48 if n <= 9 else 34
grid_px   = cell_size * n + 4

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; display: flex; flex-direction: column; align-items: center; padding: 8px 0; }}

  #grid {{
    display: grid;
    grid-template-columns: repeat({n}, {cell_size}px);
    grid-template-rows:    repeat({n}, {cell_size}px);
    border: 2.5px solid #1a1a2e;
    gap: 0;
    width: {grid_px}px;
  }}

  .cell {{
    width: {cell_size}px; height: {cell_size}px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Mono', monospace;
    font-size: {"1.1rem" if n <= 9 else ".8rem"};
    border: 1px solid #bbb;
    cursor: pointer;
    user-select: none;
    transition: background .1s;
    color: #1a1a2e;
    background: #fff;
    position: relative;
  }}
  .cell.given      {{ background: #eef2ff; font-weight: 700; cursor: default; }}
  .cell.selected   {{ background: #bfdbfe !important; outline: 2px solid #3b82f6; outline-offset: -2px; z-index: 2; }}
  .cell.peer       {{ background: #e0e7ff; }}
  .cell.wrong      {{ color: #e63946; }}
  .cell.hint-cell  {{ background: #d4f7dc; color: #2d6a4f; font-weight: 700; }}
  .cell.box-right  {{ border-right:  2.5px solid #1a1a2e; }}
  .cell.box-bottom {{ border-bottom: 2.5px solid #1a1a2e; }}

  /* Number pad */
  #numpad {{
    display: flex; flex-wrap: wrap; gap: 6px;
    justify-content: center;
    margin-top: 14px;
    width: {min(grid_px, 9 * 46)}px;
  }}
  .num-btn {{
    width: 42px; height: 42px;
    border: 2px solid #1a1a2e;
    border-radius: 8px;
    background: #fff;
    font-family: 'Space Mono', monospace;
    font-size: 1rem; font-weight: 700;
    cursor: pointer;
    transition: background .15s, transform .1s;
    color: #1a1a2e;
  }}
  .num-btn:hover  {{ background: #e0e7ff; transform: scale(1.08); }}
  .num-btn:active {{ background: #bfdbfe; }}
  .num-btn.erase  {{ color: #e63946; border-color: #e63946; }}

  #hint-label {{
    font-family: 'Space Mono', monospace;
    font-size: .8rem; color: #555;
    margin-top: 8px;
  }}
</style>
</head>
<body>

<div id="grid"></div>
<div id="numpad"></div>
<div id="hint-label">Click a cell, then press a number key or tap a button</div>

<script>
const BOARD    = {board_json};
const GIVEN    = {given_json};
const SOLUTION = {solution_json};
const HINT     = {hint_json};
const WON      = {won_json};
const N        = {n};
const BR       = {br};
const BC       = {bc};

let selected = null;   // [r, c] or null

// ── Build grid ────────────────────────────────────────────────────────────
const grid = document.getElementById('grid');

for (let r = 0; r < N; r++) {{
  for (let c = 0; c < N; c++) {{
    const td = document.createElement('div');
    td.className = 'cell';
    td.dataset.r = r;
    td.dataset.c = c;

    // Thick box borders
    if ((c + 1) % BC === 0 && c !== N - 1) td.classList.add('box-right');
    if ((r + 1) % BR === 0 && r !== N - 1) td.classList.add('box-bottom');

    if (GIVEN[r][c]) td.classList.add('given');

    if (HINT && HINT[0] === r && HINT[1] === c) td.classList.add('hint-cell');

    const v = BOARD[r][c];
    if (v !== 0) {{
      td.textContent = v;
      if (!GIVEN[r][c] && v !== SOLUTION[r][c]) td.classList.add('wrong');
    }}

    if (!WON && !GIVEN[r][c]) {{
      td.addEventListener('click', () => selectCell(r, c));
    }}

    grid.appendChild(td);
  }}
}}

// ── Build numpad ──────────────────────────────────────────────────────────
const numpad = document.getElementById('numpad');
for (let v = 1; v <= N; v++) {{
  const btn = document.createElement('button');
  btn.className = 'num-btn';
  btn.textContent = v;
  btn.addEventListener('click', () => placeValue(v));
  numpad.appendChild(btn);
}}
const erase = document.createElement('button');
erase.className = 'num-btn erase';
erase.textContent = '✕';
erase.addEventListener('click', () => placeValue(0));
numpad.appendChild(erase);

// ── Selection ─────────────────────────────────────────────────────────────
function getCell(r, c) {{
  return grid.children[r * N + c];
}}

function selectCell(r, c) {{
  // Deselect old
  grid.querySelectorAll('.selected,.peer').forEach(el => {{
    el.classList.remove('selected', 'peer');
  }});
  selected = [r, c];
  getCell(r, c).classList.add('selected');

  // Highlight peers (same row, col, box)
  for (let i = 0; i < N; i++) {{
    if (i !== c) getCell(r, i).classList.add('peer');
    if (i !== r) getCell(i, c).classList.add('peer');
  }}
  const boxR = Math.floor(r / BR) * BR;
  const boxC = Math.floor(c / BC) * BC;
  for (let dr = 0; dr < BR; dr++) {{
    for (let dc = 0; dc < BC; dc++) {{
      const pr = boxR + dr, pc = boxC + dc;
      if (pr !== r || pc !== c) getCell(pr, pc).classList.add('peer');
    }}
  }}
}}

// ── Place value ───────────────────────────────────────────────────────────
function placeValue(v) {{
  if (!selected || WON) return;
  const [r, c] = selected;
  if (GIVEN[r][c]) return;

  // Optimistic update
  const td = getCell(r, c);
  if (v === 0) {{
    td.textContent = '';
    td.classList.remove('wrong', 'hint-cell');
    BOARD[r][c] = 0;
  }} else {{
    td.textContent = v;
    BOARD[r][c] = v;
    td.classList.remove('hint-cell');
    if (v !== SOLUTION[r][c]) td.classList.add('wrong');
    else td.classList.remove('wrong');
  }}

  // Send to Streamlit
  window.parent.postMessage({{
    type: 'streamlit:setComponentValue',
    value: {{r, c, v}}
  }}, '*');
}}

// ── Keyboard ──────────────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {{
  if (!selected) return;
  const [r, c] = selected;
  if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {{
    placeValue(0); return;
  }}
  const num = parseInt(e.key);
  if (!isNaN(num) && num >= 1 && num <= N) {{
    placeValue(num);
  }}
  // Arrow key navigation
  const moves = {{ ArrowUp:[-1,0], ArrowDown:[1,0], ArrowLeft:[0,-1], ArrowRight:[0,1] }};
  if (moves[e.key]) {{
    const [dr, dc] = moves[e.key];
    const nr = Math.max(0, Math.min(N-1, r+dr));
    const nc = Math.max(0, Math.min(N-1, c+dc));
    if (!GIVEN[nr][nc]) selectCell(nr, nc);
    else selectCell(nr, nc);   // still select even if given, just can't type
    e.preventDefault();
  }}
}});
</script>
</body>
</html>
"""

# Height: grid + numpad + label
component_height = grid_px + 80 + 20 + 30

result = components.html(html, height=component_height, scrolling=False)

# When the component sends a value back, store and rerun
if result is not None and isinstance(result, dict):
    st.session_state.last_move = result
    st.rerun()

# ── Auto-refresh timer ────────────────────────────────────────────────────────
if st.session_state.running and not st.session_state.won:
    time.sleep(1)
    st.rerun()
