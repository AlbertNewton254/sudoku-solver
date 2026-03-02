# Sudoku Solver

A modern 9×9 Sudoku solver using Prolog's constraint logic. Originally developed for the Logic Applied to Computing course at UFPB (Federal University of Paraíba, Brazil), this project demonstrates practical applications of declarative programming and automated reasoning.

## Features

- **Modern Web Interface**: Beautiful, interactive Streamlit-based UI
  - Click-to-edit cells
  - Real-time validation
  - Visual distinction between clues and solutions
  - Pre-loaded example puzzles (Easy, Medium, Hard)

- **Efficient Solving**: Uses SWI-Prolog's CLP(FD) library for constraint-based solving
  - Constraint propagation with backtracking
  - Typically solves puzzles in under 1 second
  - Guaranteed to find solution if one exists

- **Docker-Ready**: Containerized deployment with all dependencies included

- **Direct Prolog Integration**: No Python fallback - pure Prolog solving power

## Requirements

### Quick Start (Docker - Recommended)

- **Docker**: For containerized deployment with all dependencies
  ```bash
  # Build and run in one command
  docker build -t sudoku-solver . && docker run -p 8501:8501 sudoku-solver
  ```

### Local Development

- **SWI-Prolog**: Version 7.0 or higher
  ```bash
  # Ubuntu/Debian
  sudo apt-get install swi-prolog

  # macOS
  brew install swi-prolog

  # Fedora
  sudo dnf install pl
  ```

- **Python 3.12+**: With Streamlit
  ```bash
  pip install -r requirements.txt
  ```

## Installation & Usage

### Option 1: Docker (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/AlbertNewton/sudoku-solver.git
   cd sudoku-solver
   ```

2. Build and run the Docker container:
   ```bash
   docker build -t sudoku-solver .
   docker run -p 8501:8501 sudoku-solver
   ```

3. Open your browser to `http://localhost:8501`

### Option 2: Local Development

1. Clone and install dependencies:
   ```bash
   git clone https://github.com/AlbertNewton/sudoku-solver.git
   cd sudoku-solver
   pip install -r requirements.txt
   ```

2. Verify SWI-Prolog is installed:
   ```bash
   swipl --version
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

4. Open your browser to `http://localhost:8501`

## Using the Web Interface

1. **Enter a Puzzle**: Click any cell and type a number (1-9), or leave empty
2. **Try Examples**: Click Easy, Medium, or Hard for pre-loaded puzzles
3. **Solve**: Click the ▶ Solve button
4. **View Solution**: Original clues appear in dark blue, solved cells in green
5. **Try Again**: Click 🔄 Try Again to modify the puzzle
6. **Clear**: Click 🗑️ Clear to start fresh

### Direct Prolog Interface (CLI)

Run the interactive Prolog menu:
```bash
swipl -q -g main -t halt solver.pl
```

The menu offers:
1. Solve example puzzles (easy, medium, hard)
2. Enter a puzzle manually
3. About information
0. Exit

### Programmatic Prolog Usage

Solve a puzzle programmatically:
```bash
swipl -q -g "solve_and_print([[_,_,3,_,2,_,6,_,_],[9,_,_,3,_,5,_,_,1],...])" -t halt solver.pl
```

Or use example puzzles:
```bash
swipl -q -g "puzzle(easy, B), sudoku(B), display_board(B)" -t halt solver.pl
```

## Example Puzzles

The application includes three built-in example puzzles:

### Easy Puzzle
```
_ _ 3 | _ 2 _ | 6 _ _
9 _ _ | 3 _ 5 | _ _ 1
_ _ 1 | 8 _ 6 | 4 _ _
------+-------+------
_ _ 8 | 1 _ 2 | 9 _ _
7 _ _ | _ _ _ | _ _ 8
_ _ 6 | 7 _ 8 | 2 _ _
------+-------+------
_ _ 2 | 6 _ 9 | 5 _ _
8 _ _ | 2 _ 3 | _ _ 9
_ _ 5 | _ 1 _ | 3 _ _
```

### Medium & Hard Puzzles
Access these directly in the web interface by clicking the respective buttons.

## How It Works

### Prolog Core (solver.pl)

The solver uses Constraint Logic Programming over Finite Domains (CLP(FD)):

1. **Domain Definition**: Each cell must contain a digit from 1 to 9
2. **Row Constraints**: All cells in a row must be distinct
3. **Column Constraints**: All cells in a column must be distinct
4. **Region Constraints**: All cells in each 3×3 block must be distinct
5. **Labeling**: Find values that satisfy all constraints using backtracking

Key predicates:
- `sudoku/1`: Main solver predicate
- `valid_rows/1`, `valid_columns/1`, `valid_regions/1`: Constraint validators
- `display_board/1`: Pretty-prints the board

### Streamlit Web Interface (app.py)

The web interface provides:
- **Interactive Grid**: Click-to-edit cells with real-time validation
- **Visual Feedback**: Distinguishes between clues and solutions
- **Prolog Integration**: Calls solver.pl directly via subprocess
- **Session Management**: Maintains puzzle state across interactions

## Project Structure

```
sudoku-solver/
├── solver.pl           # Prolog solver core with CLP(FD)
├── app.py              # Streamlit web interface
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
└── README.md           # This file
```

## Technical Details

**Algorithm**: Constraint propagation with backtracking search
- Uses SWI-Prolog's `clpfd` library
- First-fail strategy for efficient variable assignment
- Guarantees finding a solution if one exists

**Complexity**:
- Worst case: $O(9^n)$ where $n$ is the number of empty cells
- Typical performance: < 1 second for most puzzles due to constraint propagation

## Architecture

```
┌─────────────────┐
│   app.py        │  Streamlit Web UI
│   (Python)      │  - Interactive grid
└────────┬────────┘  - Session management
         │
         │ subprocess.run()
         │
┌────────▼────────┐
│   solver.pl     │  Prolog Solver
│   (SWI-Prolog)  │  - CLP(FD) constraints
└─────────────────┘  - Backtracking search

┌─────────────────┐
│   Dockerfile    │  Containerization
│                 │  - SWI-Prolog + Streamlit
└─────────────────┘  - Production ready
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Originally developed as a final project for Logic Applied to Computing course at UFPB, 2026.*
