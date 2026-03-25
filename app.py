import streamlit as st
import subprocess
import copy
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sudoku Solver", page_icon="🧩", layout="centered")

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

/* ── Root & background ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0f !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: #0d0d0f;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Typography baseline ── */
html, body, * { font-family: 'Space Mono', monospace !important; color: #e8e6e0; }

/* Force primary button text black — * selector above bleeds into inner <p> */
.stButton button[kind="primary"] p,
.stButton button[kind="primary"] span,
.stButton button[kind="primary"] * {
    color: #0d0d0f !important;
}

/* ── Title block ── */
.solver-header {
    text-align: center;
    padding: 2.5rem 0 1.2rem;
}
.solver-header h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #f5f0e8;
    margin: 0;
    line-height: 1;
}
.solver-header h1 span { color: #c8f135; }
.solver-sub {
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #555;
    margin-top: 0.5rem;
}

/* ── Control buttons ── */
.stButton button {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    border: 1px solid #2a2a2e !important;
    background: #141417 !important;
    color: #888 !important;
    padding: 0.5rem 0 !important;
    transition: all 0.15s ease !important;
}
.stButton button:hover {
    border-color: #c8f135 !important;
    color: #c8f135 !important;
    background: #141417 !important;
}
/* Primary / Solve button */
.stButton button[kind="primary"] {
    background: #c8f135 !important;
    border-color: #c8f135 !important;
    color: #0d0d0f !important;
    font-weight: 900 !important;
}
.stButton button[kind="primary"]:hover {
    background: #d9ff50 !important;
    border-color: #d9ff50 !important;
    color: #0d0d0f !important;
}

/* ── Dividers ── */
hr { border-color: #1e1e22 !important; margin: 1rem 0 !important; }

/* ── Text inputs (cells) ── */
div[data-testid="column"] { padding: 0 !important; }

/* Strip all padding/margin from every wrapper layer */
.stTextInput,
.stTextInput > div,
.stTextInput > div > div {
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    height: 54px !important;
}

.stTextInput > div > div > input {
    text-align: center !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 800 !important;
    color: #f5f0e8 !important;
    background: #141417 !important;
    border: 1px solid #222226 !important;
    border-radius: 3px !important;
    height: 54px !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    caret-color: #c8f135;
    transition: border-color 0.15s, background 0.15s;
}
.stTextInput > div > div > input:focus {
    border-color: #c8f135 !important;
    background: #1a1a1e !important;
    box-shadow: 0 0 0 2px rgba(200, 241, 53, 0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: #2a2a30 !important; }

/* ── Section label ── */
.grid-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #444;
    margin-bottom: 0.8rem;
}

/* ── 3x3 box separators ── */
.box-sep-h {
    height: 3px;
    background: linear-gradient(90deg, transparent, #c8f135 20%, #c8f135 80%, transparent);
    margin: 2px 0;
    border-radius: 2px;
}
.box-sep-v-spacer { margin: 3px 0; }

/* Vertical separators after columns 3 and 6 */
div[data-testid="stHorizontalBlock"] > div:nth-child(3),
div[data-testid="stHorizontalBlock"] > div:nth-child(6) {
    border-right: 3px solid #c8f135 !important;
    margin-right: 3px !important;
}

/* ── Solution cell ── */
.sol-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 54px;
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    border-radius: 3px;
    border: 1px solid #1e1e22;
}
.sol-clue  { color: #f5f0e8; background: #1a1a1e; }
.sol-found { color: #c8f135; background: #141f00; border-color: #2a3d00; }

/* ── Status messages ── */
.stAlert {
    border-radius: 4px !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.04em !important;
}

/* ── Streamlit misc overrides ── */
[data-testid="stDecoration"] { display: none; }
footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="solver-header">
    <h1>SUDOKU<span>.</span>SOLVER</h1>
    <p class="solver-sub">Powered by SWI-Prolog CLP(FD)</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "board" not in st.session_state:
    st.session_state.board = [[0] * 9 for _ in range(9)]
if "solution" not in st.session_state:
    st.session_state.solution = None
if "error" not in st.session_state:
    st.session_state.error = None
if "cell_errors" not in st.session_state:
    st.session_state.cell_errors = []

# ── Helpers ───────────────────────────────────────────────────────────────────
def board_from_session() -> tuple[list[list[int]], list[str]]:
    board, invalid_cells = [], []
    for r in range(9):
        row = []
        for c in range(9):
            val = st.session_state.get(f"cell_{r}_{c}", "")
            if isinstance(val, str) and val.strip() == "":
                row.append(0)
            elif isinstance(val, str) and val.isdigit() and 1 <= int(val) <= 9:
                row.append(int(val))
            else:
                row.append(0)
                invalid_cells.append(f"R{r+1}C{c+1}")
        board.append(row)
    return board, invalid_cells


def validate_cell_input(key: str) -> None:
    val = st.session_state.get(key, "")
    if val and (not val.isdigit() or not 1 <= int(val) <= 9):
        st.session_state[key] = ""
        st.session_state.cell_errors.append(key)


def _load_puzzle(difficulty: str) -> None:
    puzzle, err = get_puzzle_from_prolog(difficulty)
    if puzzle:
        st.session_state.board = copy.deepcopy(puzzle)
        st.session_state.solution = None
        st.session_state.error = None
        for r in range(9):
            for c in range(9):
                val = puzzle[r][c]
                st.session_state[f"cell_{r}_{c}"] = str(val) if val != 0 else ""
    else:
        st.session_state.error = f"Failed to load {difficulty} puzzle. {err or ''}"


def _clear_board() -> None:
    st.session_state.board = [[0] * 9 for _ in range(9)]
    st.session_state.solution = None
    st.session_state.error = None
    st.session_state.cell_errors = []
    for r in range(9):
        for c in range(9):
            st.session_state[f"cell_{r}_{c}"] = ""


# ── Prolog interface ──────────────────────────────────────────────────────────
_SOLVER_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_prolog(goal: str, timeout: int = 10) -> tuple[str | None, str | None]:
    try:
        result = subprocess.run(
            ["swipl", "-q", "-g", goal, "-t", "halt", "solver.pl"],
            capture_output=True, text=True, timeout=timeout, cwd=_SOLVER_DIR,
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            return None, msg or "Prolog process exited with an error."
        return result.stdout, None
    except subprocess.TimeoutExpired:
        return None, "Prolog solver timed out."
    except FileNotFoundError:
        return None, "SWI-Prolog not found. Make sure 'swipl' is installed."
    except Exception as exc:
        return None, str(exc)


def _parse_board_lines(output: str) -> list[list[int]] | None:
    board = []
    for line in output.strip().splitlines():
        line = line.strip().strip("[]")
        if not line:
            continue
        try:
            cells = [int(x.strip()) for x in line.split(",")]
        except ValueError:
            return None
        if len(cells) == 9:
            board.append(cells)
    return board if len(board) == 9 else None


def get_puzzle_from_prolog(difficulty: str) -> tuple[list[list[int]] | None, str | None]:
    stdout, err = _run_prolog(f"print_puzzle_as_list({difficulty})", timeout=5)
    if stdout is None:
        return None, err
    board = _parse_board_lines(stdout)
    if board is None:
        return None, "Could not parse puzzle output from Prolog."
    return board, None


def solve_prolog(board: list[list[int]]) -> tuple[list[list[int]] | None, str | None]:
    rows = []
    for row in board:
        cells = ",".join(str(v) if v != 0 else "_" for v in row)
        rows.append(f"[{cells}]")
    board_str = "[" + ",".join(rows) + "]"
    stdout, err = _run_prolog(f"solve_and_print({board_str})", timeout=10)
    if stdout is None:
        return None, err
    solution = _parse_board_lines(stdout)
    if solution is None:
        return None, "Could not parse solution output from Prolog."
    return solution, None


# ── Control bar ───────────────────────────────────────────────────────────────
col_clear, col_easy, col_medium, col_hard, col_solve = st.columns(5)

with col_clear:
    if st.button("✕  Clear", use_container_width=True):
        _clear_board()
        st.rerun()

for col, (label, difficulty) in zip(
    [col_easy, col_medium, col_hard],
    [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")],
):
    with col:
        if st.button(label, use_container_width=True):
            _load_puzzle(difficulty)
            st.rerun()

with col_solve:
    solve_clicked = st.button("▶  Solve", use_container_width=True, type="primary")

st.divider()

# ── Cell-error flush ──────────────────────────────────────────────────────────
if st.session_state.cell_errors:
    bad = ", ".join(st.session_state.cell_errors)
    st.warning(f"Only digits 1–9 are allowed. Cleared: {bad}")
    st.session_state.cell_errors = []

# ── Grid label ────────────────────────────────────────────────────────────────
st.markdown('<p class="grid-label">Enter your puzzle — click a cell to edit (1–9)</p>',
            unsafe_allow_html=True)

# ── Grid ──────────────────────────────────────────────────────────────────────
for r in range(9):
    # Bold separator every 3 rows
    if r in {3, 6}:
        st.markdown('<div class="box-sep-h"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="box-sep-v-spacer"></div>', unsafe_allow_html=True)

    cols = st.columns(9, gap="small")

    for c in range(9):
        cell_key = f"cell_{r}_{c}"
        with cols[c]:
            if cell_key not in st.session_state:
                v = st.session_state.board[r][c]
                st.session_state[cell_key] = str(v) if v != 0 else ""

            if st.session_state.solution:
                val = st.session_state.solution[r][c]
                is_clue = st.session_state.board[r][c] != 0
                cls = "sol-clue" if is_clue else "sol-found"
                st.markdown(
                    f"<div class='sol-cell {cls}'>{val}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.text_input(
                    label=f"r{r}c{c}",
                    key=cell_key,
                    label_visibility="collapsed",
                    max_chars=1,
                    placeholder="·",
                    on_change=validate_cell_input,
                    args=(cell_key,),
                )

st.divider()

# ── Try Again ─────────────────────────────────────────────────────────────────
if st.session_state.solution:
    if st.button("↩  Try Again", use_container_width=False):
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()

# ── Solve logic ───────────────────────────────────────────────────────────────
if solve_clicked:
    current_board, invalid_cells = board_from_session()

    if invalid_cells:
        st.warning(f"Invalid input in cells: {', '.join(invalid_cells)}. Only digits 1–9 are allowed.")
        st.stop()

    if all(v == 0 for row in current_board for v in row):
        st.warning("Please enter at least one clue.")
        st.stop()

    st.session_state.board = current_board
    st.session_state.solution = None
    st.session_state.error = None

    with st.spinner("Solving…"):
        solution, err = solve_prolog(current_board)

    if solution:
        st.session_state.solution = solution
    else:
        st.session_state.error = f"Could not solve puzzle. {err or 'No solution exists.'}"

    st.rerun()

# ── Status messages ───────────────────────────────────────────────────────────
if st.session_state.solution:
    st.success("✅  Solved! Clues in white · answers in green.")

if st.session_state.error:
    st.error(st.session_state.error)