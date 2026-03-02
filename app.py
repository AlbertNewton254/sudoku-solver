import streamlit as st
import subprocess
import copy
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sudoku Solver", page_icon="🧩", layout="centered")

st.title("🧩 Sudoku Solver")
st.caption("Powered by SWI-Prolog CLP(FD)")

# ── Session state ─────────────────────────────────────────────────────────────
if "board" not in st.session_state:
    st.session_state.board = [[0]*9 for _ in range(9)]
if "solution" not in st.session_state:
    st.session_state.solution = None
if "error" not in st.session_state:
    st.session_state.error = None

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


def get_puzzle_from_prolog(difficulty):
    """
    Fetch a puzzle from Prolog using the puzzle/2 predicate.

    Args:
        difficulty: one of 'easy', 'medium', or 'hard'

    Returns:
        9x9 list of lists with integers 0-9 (0 = empty), or None on error
    """
    goal = f"print_puzzle_as_list({difficulty})"

    try:
        result = subprocess.run(
            ["swipl", "-q", "-g", goal, "-t", "halt", "solver.pl"],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode != 0:
            return None

        # Parse output: each line is like "[0,0,3,0,2,0,6,0,0]"
        board = []
        for line in result.stdout.strip().splitlines():
            line = line.strip().strip("[]")
            if line:
                cells = [int(cell.strip()) for cell in line.split(",")]
                if len(cells) == 9:
                    board.append(cells)

        return board if len(board) == 9 else None

    except Exception:
        return None



# ── Prolog solver ─────────────────────────────────────────────────────────────

def solve_prolog(board):
    """
    Solves a Sudoku board using the solver.pl Prolog solver.

    Args:
        board: 9x9 list of lists with integers 0-9 (0 = empty)

    Returns:
        tuple: (solution, error) where solution is 9x9 list or None,
               and error is error message or None
    """
    # Convert board to Prolog format: [[1,2,_,...],[...],...]
    board_rows = []
    for row in board:
        cells = ",".join(str(v) if v != 0 else "_" for v in row)
        board_rows.append(f"[{cells}]")
    board_str = "[" + ",".join(board_rows) + "]"

    # Build the goal to call solve_and_print/1
    goal = f"solve_and_print({board_str})"

    try:
        result = subprocess.run(
            ["swipl", "-q", "-g", goal, "-t", "halt", "solver.pl"],
            capture_output=True, text=True, timeout=10,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode != 0:
            error_msg = result.stdout + result.stderr
            return None, error_msg if error_msg else "Prolog solver failed"

        # Parse output: each line is like "[4,8,3,9,2,1,6,5,7]"
        solution = []
        for line in result.stdout.strip().splitlines():
            line = line.strip().strip("[]")
            if line:
                nums = [int(x.strip()) for x in line.split(",")]
                if len(nums) == 9:
                    solution.append(nums)

        if len(solution) == 9:
            return solution, None
        return None, "Could not parse Prolog output"

    except subprocess.TimeoutExpired:
        return None, "Prolog solver timed out"
    except FileNotFoundError:
        return None, "SWI-Prolog not found. Make sure 'swipl' is installed."
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
        # Clear all cell inputs
        for r in range(9):
            for c in range(9):
                st.session_state[f"cell_{r}_{c}"] = ""
        st.rerun()
with col2:
    if st.button("Easy", use_container_width=True):
        puzzle = get_puzzle_from_prolog('easy')
        if puzzle:
            st.session_state.board = copy.deepcopy(puzzle)
            st.session_state.solution = None
            st.session_state.error = None
            # Populate cell inputs with example
            for r in range(9):
                for c in range(9):
                    val = puzzle[r][c]
                    st.session_state[f"cell_{r}_{c}"] = str(val) if val != 0 else ""
            st.rerun()
with col3:
    if st.button("Medium", use_container_width=True):
        puzzle = get_puzzle_from_prolog('medium')
        if puzzle:
            st.session_state.board = copy.deepcopy(puzzle)
            st.session_state.solution = None
            st.session_state.error = None
            # Populate cell inputs with example
            for r in range(9):
                for c in range(9):
                    val = puzzle[r][c]
                    st.session_state[f"cell_{r}_{c}"] = str(val) if val != 0 else ""
            st.rerun()
with col4:
    if st.button("Hard", use_container_width=True):
        puzzle = get_puzzle_from_prolog('hard')
        if puzzle:
            st.session_state.board = copy.deepcopy(puzzle)
            st.session_state.solution = None
            st.session_state.error = None
            # Populate cell inputs with example
            for r in range(9):
                for c in range(9):
                    val = puzzle[r][c]
                    st.session_state[f"cell_{r}_{c}"] = str(val) if val != 0 else ""
            st.rerun()
with col5:
    solve_clicked = st.button("▶ Solve", use_container_width=True, type="primary")

st.divider()

# Interactive 9×9 Sudoku Grid
st.markdown("**Enter your puzzle** — click on any cell to edit (1-9, or leave empty):")

# Custom CSS for better grid appearance
st.markdown("""
<style>
div[data-testid="column"] {
    padding: 0 !important;
}
.stTextInput > div > div > input {
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    padding: 12px 0;
    height: 52px;
}
</style>
""", unsafe_allow_html=True)

# Render the interactive grid with text inputs
for r in range(9):
    cols = st.columns([1]*9, gap="small")
    for c in range(9):
        with cols[c]:
            # Initialize session state for this cell if not exists
            cell_key = f"cell_{r}_{c}"
            if cell_key not in st.session_state:
                current_val = st.session_state.board[r][c]
                st.session_state[cell_key] = str(current_val) if current_val != 0 else ""

            # Show solution if available
            if st.session_state.solution:
                solution_val = st.session_state.solution[r][c]
                is_clue = st.session_state.board[r][c] != 0
                if is_clue:
                    st.markdown(f"<div style='text-align:center; font-size:24px; font-weight:700; color:#1e3a5f; padding:14px 0;'>{solution_val}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center; font-size:24px; font-weight:700; color:#16a34a; padding:14px 0;'>{solution_val}</div>", unsafe_allow_html=True)
            else:
                st.text_input(
                    label=f"r{r}c{c}",
                    key=cell_key,
                    label_visibility="collapsed",
                    max_chars=1,
                    placeholder="·",
                )

    # Add visual separator after every 3rd row
    if r in [2, 5]:
        st.markdown("<hr style='margin: 8px 0; border: 1px solid #333;'>", unsafe_allow_html=True)
    elif r < 8:
        st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)

st.divider()

# Action buttons
col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    if st.session_state.solution and st.button("🔄 Try Again", use_container_width=True):
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()

# Solve logic
if solve_clicked:
    current_board = board_from_session()
    st.session_state.board = current_board
    st.session_state.solution = None
    st.session_state.error = None

    # Validate board is not empty
    if all(v == 0 for row in current_board for v in row):
        st.warning("Please enter at least one clue.")
        st.stop()

    solution, err = solve_prolog(current_board)
    if solution:
        st.session_state.solution = solution
    else:
        st.session_state.error = f"Could not solve puzzle. {err if err else 'No solution exists.'}"

    st.rerun()

# Status messages
if st.session_state.solution:
    st.success("✅ Solved! Click 'Try Again' to edit the puzzle.")

if st.session_state.error:
    st.error(st.session_state.error)