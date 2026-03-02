import streamlit as st
import subprocess
import shutil
import copy

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sudoku Solver", page_icon="🧩", layout="centered")

st.title("🧩 Sudoku Solver")
st.caption("Powered by SWI-Prolog CLP(FD) — with a Python backtracking fallback")

# ── Example puzzles ───────────────────────────────────────────────────────────
EXAMPLES = {
    "Easy": [
        [0,0,3,0,2,0,6,0,0],
        [9,0,0,3,0,5,0,0,1],
        [0,0,1,8,0,6,4,0,0],
        [0,0,8,1,0,2,9,0,0],
        [7,0,0,0,0,0,0,0,8],
        [0,0,6,7,0,8,2,0,0],
        [0,0,2,6,0,9,5,0,0],
        [8,0,0,2,0,3,0,0,9],
        [0,0,5,0,1,0,3,0,0],
    ],
    "Medium": [
        [0,0,0,2,6,0,7,0,1],
        [6,8,0,0,7,0,0,9,0],
        [1,9,0,0,0,4,5,0,0],
        [8,2,0,1,0,0,0,4,0],
        [0,0,4,6,0,2,9,0,0],
        [0,5,0,0,0,3,0,2,8],
        [0,0,9,3,0,0,0,7,4],
        [0,4,0,0,5,0,0,3,6],
        [7,0,3,0,1,8,0,0,0],
    ],
    "Hard": [
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,3,0,8,5],
        [0,0,1,0,2,0,0,0,0],
        [0,0,0,5,0,7,0,0,0],
        [0,0,4,0,0,0,1,0,0],
        [0,9,0,0,0,0,0,0,0],
        [5,0,0,0,0,0,0,7,3],
        [0,0,2,0,1,0,0,0,0],
        [0,0,0,0,4,0,0,0,9],
    ],
}

# ── Session state ─────────────────────────────────────────────────────────────
if "board" not in st.session_state:
    st.session_state.board = [[0]*9 for _ in range(9)]
if "solution" not in st.session_state:
    st.session_state.solution = None
if "error" not in st.session_state:
    st.session_state.error = None
if "solver_used" not in st.session_state:
    st.session_state.solver_used = None

# ── Helpers ───────────────────────────────────────────────────────────────────

def board_from_session():
    """Read current 9x9 board from session state widget keys."""
    board = []
    for r in range(9):
        row = []
        for c in range(9):
            val = st.session_state.get(f"cell_{r}_{c}", "")
            try:
                n = int(val)
                row.append(n if 1 <= n <= 9 else 0)
            except (ValueError, TypeError):
                row.append(0)
        board.append(row)
    return board

# ── Pure Python backtracking solver ──────────────────────────────────────────

def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True

def solve_python(board):
    board = copy.deepcopy(board)
    empty = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]

    def backtrack(idx):
        if idx == len(empty):
            return True
        r, c = empty[idx]
        for num in range(1, 10):
            if is_valid(board, r, c, num):
                board[r][c] = num
                if backtrack(idx + 1):
                    return True
                board[r][c] = 0
        return False

    if backtrack(0):
        return board
    return None

# ── Prolog solver ─────────────────────────────────────────────────────────────

def board_to_prolog_list(board):
    cells = []
    for row in board:
        for val in row:
            cells.append(str(val) if val != 0 else "_")
    return "[" + ",".join(cells) + "]"

def solve_prolog(board):
    prolog_list = board_to_prolog_list(board)
    goal = (
        f"use_module(library(clpfd)), "
        f"B = {prolog_list}, "
        f"Rows = [R1,R2,R3,R4,R5,R6,R7,R8,R9], "
        f"append(Rows, B), "
        f"maplist(ins(1..9), B), "
        f"maplist(all_distinct, Rows), "
        f"transpose(Rows, Cols), maplist(all_distinct, Cols), "
        f"Rows = [A,B2,C,D,E,F,G,H,I], "
        f"blocks(A,B2,C), blocks(D,E,F), blocks(G,H,I), "
        f"maplist(label, Rows), "
        f"maplist(writeln, Rows), halt."
    )
    # Simpler self-contained goal using the atva02.pl approach
    board_rows = []
    for row in board:
        cells = ",".join(str(v) if v != 0 else "_" for v in row)
        board_rows.append(f"[{cells}]")
    rows_str = "[" + ",".join(board_rows) + "]"

    goal = (
        "use_module(library(clpfd)),"
        f"Board = {rows_str},"
        "append(Board, Vs), Vs ins 1..9,"
        "maplist(all_distinct, Board),"
        "transpose(Board, Cols), maplist(all_distinct, Cols),"
        "Board = [R1,R2,R3,R4,R5,R6,R7,R8,R9],"
        "blocks(R1,R2,R3), blocks(R4,R5,R6), blocks(R7,R8,R9),"
        "maplist(label, Board),"
        "maplist(writeln, Board), halt."
    )

    blocks_def = (
        ":- meta_predicate blocks(+,+,+). "
        "blocks([],[],[]). "
        "blocks([A,B,C|T1],[D,E,F|T2],[G,H,I|T3]) :- "
        "all_distinct([A,B,C,D,E,F,G,H,I]), blocks(T1,T2,T3)."
    )

    prolog_program = f":- use_module(library(clpfd)).\n{blocks_def}\n:- {goal}\n"

    import tempfile, os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as f:
        f.write(prolog_program)
        fname = f.name

    try:
        result = subprocess.run(
            ["swipl", "-q", "-f", fname],
            capture_output=True, text=True, timeout=10
        )
        os.unlink(fname)
        if result.returncode != 0:
            return None, result.stderr
        # Parse output: each line is like "[4,8,3,9,2,1,6,5,7]"
        solution = []
        for line in result.stdout.strip().splitlines():
            line = line.strip().strip("[]")
            nums = [int(x) for x in line.split(",")]
            if len(nums) == 9:
                solution.append(nums)
        if len(solution) == 9:
            return solution, None
        return None, "Could not parse Prolog output"
    except subprocess.TimeoutExpired:
        os.unlink(fname)
        return None, "Prolog solver timed out"
    except Exception as e:
        return None, str(e)

# ── UI ────────────────────────────────────────────────────────────────────────

# Top controls
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col1:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.board = [[0]*9 for _ in range(9)]
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()
with col2:
    if st.button("Easy", use_container_width=True):
        st.session_state.board = copy.deepcopy(EXAMPLES["Easy"])
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()
with col3:
    if st.button("Medium", use_container_width=True):
        st.session_state.board = copy.deepcopy(EXAMPLES["Medium"])
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()
with col4:
    if st.button("Hard", use_container_width=True):
        st.session_state.board = copy.deepcopy(EXAMPLES["Hard"])
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()
with col5:
    solve_clicked = st.button("▶ Solve", use_container_width=True, type="primary")

st.divider()

# 9×9 grid
display = st.session_state.solution if st.session_state.solution else st.session_state.board
clue_board = st.session_state.board  # original clues (non-zero = clue)

BOX_COLORS = {
    (0,0): "#EEF2FF", (0,1): "#FFF7ED", (0,2): "#EEF2FF",
    (1,0): "#FFF7ED", (1,1): "#EEF2FF", (1,2): "#FFF7ED",
    (2,0): "#EEF2FF", (2,1): "#FFF7ED", (2,2): "#EEF2FF",
}

# Render grid with custom styling
grid_html = """
<style>
.sudoku-grid { border-collapse: collapse; margin: 0 auto; }
.sudoku-grid td {
    width: 46px; height: 46px;
    text-align: center; vertical-align: middle;
    font-size: 20px; font-weight: 600;
    border: 1px solid #ccc;
    cursor: default;
}
.sudoku-grid tr:nth-child(3n) td { border-bottom: 2.5px solid #333; }
.sudoku-grid tr:nth-child(3n+1) td { border-top: 2.5px solid #333; }
.sudoku-grid td:nth-child(3n) { border-right: 2.5px solid #333; }
.sudoku-grid td:nth-child(3n+1) { border-left: 2.5px solid #333; }
.cell-clue { color: #1e3a5f; }
.cell-solved { color: #16a34a; }
.cell-empty { color: #9ca3af; }
</style>
<table class="sudoku-grid">
"""
for r in range(9):
    grid_html += "<tr>"
    for c in range(9):
        box = (r // 3, c // 3)
        bg = BOX_COLORS[box]
        val = display[r][c]
        is_clue = clue_board[r][c] != 0
        is_solved_cell = (not is_clue) and val != 0

        if val == 0:
            cell_class = "cell-empty"
            text = "·"
        elif is_clue:
            cell_class = "cell-clue"
            text = str(val)
        else:
            cell_class = "cell-solved"
            text = str(val)

        grid_html += f'<td style="background:{bg}"><span class="{cell_class}">{text}</span></td>'
    grid_html += "</tr>"
grid_html += "</table>"

st.markdown(grid_html, unsafe_allow_html=True)

st.divider()

# Input area
st.markdown("**Edit puzzle** — enter digits 1–9, use 0 or leave blank for empty cells:")

input_cols = st.columns(9)
for r in range(9):
    for c in range(9):
        current_val = st.session_state.board[r][c]
        display_val = str(current_val) if current_val != 0 else ""
        input_cols[c].text_input(
            label=f"r{r}c{c}",
            value=display_val,
            key=f"cell_{r}_{c}",
            label_visibility="collapsed",
            max_chars=1,
        )

# Solve logic
if solve_clicked:
    current_board = board_from_session()
    st.session_state.board = current_board
    st.session_state.solution = None
    st.session_state.error = None

    swipl_available = shutil.which("swipl") is not None

    if swipl_available:
        solution, err = solve_prolog(current_board)
        if solution:
            st.session_state.solution = solution
            st.session_state.solver_used = "Prolog (CLP/FD)"
        else:
            # fallback
            solution = solve_python(current_board)
            if solution:
                st.session_state.solution = solution
                st.session_state.solver_used = "Python (backtracking fallback)"
            else:
                st.session_state.error = f"No solution found. Prolog error: {err}"
    else:
        solution = solve_python(current_board)
        if solution:
            st.session_state.solution = solution
            st.session_state.solver_used = "Python (backtracking — swipl not found)"
        else:
            st.session_state.error = "No solution found for this puzzle."

    st.rerun()

# Status messages
if st.session_state.solution:
    st.success(f"✅ Solved! ({st.session_state.solver_used})")

if st.session_state.error:
    st.error(st.session_state.error)

# Solver availability info
swipl_ok = shutil.which("swipl") is not None
if swipl_ok:
    st.info("🔵 SWI-Prolog detected — Prolog CLP(FD) solver will be used.")
else:
    st.warning("⚠️ SWI-Prolog not found — using pure Python backtracking solver. Install with: `sudo apt install swi-prolog`")