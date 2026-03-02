"""
sudoku_solver.py

Solves 9x9 Sudoku puzzles using SWI-Prolog with clpfd.
Accepts multiple input formats and preserves the original format in output.

Supported input formats per line:
  - Compact:       123456789
  - Spaced:        1 2 3 4 5 6 7 8 9
  - Separated:     1,2,3,4,5,6,7,8,9
  - Mixed:         1 2,3 4 5,6 7 8 9
  - With dots:     ..3.2.6..   (dot = empty)
  - With zeros:    003020600   (zero = empty)
  - Combined:      0 0 3 0 2 0 6 0 0

Usage:
  python3 sudoku_solver.py                          # Interactive mode
  python3 sudoku_solver.py --input puzzle.txt       # Read file, print solution to stdout
  python3 sudoku_solver.py --output solved.txt      # Interactive, save to file
  python3 sudoku_solver.py --input puzzle.txt --output solved.txt  # File to file

The output format always matches the input format.
Requires SWI-Prolog with atva02.pl in the same directory.
"""

import sys
import re
import subprocess
import os
import argparse
from typing import Optional, List

BOARD_SIZE = 9
EMPTY = 0
PROLOG_SOLVER = "atva02.pl"

class FormatDetector:
    """Detects and preserves the format of each line."""

    def __init__(self):
        self.line_formats: List[str] = []
        self.original_lines: List[str] = []

    def detect_format(self, line: str) -> str:
        line = line.strip()

        if not line or line.startswith(('#', '%', '//')) or re.fullmatch(r'[-=+|_ ]+', line):
            return 'ignore'

        if '.' in line:
            if re.match(r'^[0-9.]+$', line.replace(' ', '')):
                return 'dots'

        if ',' in line and not re.search(r'\d,\d', line):
            return 'separated'

        if ' ' in line.strip():
            tokens = line.split()
            if all(re.match(r'^[0-9.]$', t) for t in tokens if t):
                return 'spaced'

        if re.match(r'^[0-9]+$', line) and len(line) == BOARD_SIZE:
            return 'compact'

        if re.match(r'^[0-9.]+$', line) and len(line) == BOARD_SIZE:
            return 'dots'

        return 'mixed'

    def record_line(self, line: str, format_type: str):
        if format_type != 'ignore':
            self.line_formats.append(format_type)
            self.original_lines.append(line.rstrip('\n'))

    def get_output_line(self, board_row: List[int], original_format: str, original_line: str) -> str:
        if original_format == 'compact':
            return ''.join(str(cell) for cell in board_row)

        elif original_format == 'dots':
            return ''.join('.' if cell == EMPTY else str(cell) for cell in board_row)

        elif original_format == 'spaced':
            return ' '.join(str(cell) for cell in board_row)

        elif original_format == 'separated':
            return ','.join(str(cell) for cell in board_row)

        elif original_format == 'mixed':
            # Reconstruct using original as template to preserve spacing/punctuation
            result = original_line
            digit_positions = []

            for i, char in enumerate(original_line):
                if char.isdigit() or char == '.':
                    digit_positions.append(i)

            if len(digit_positions) == BOARD_SIZE:
                result_list = list(original_line)
                for pos, value in zip(digit_positions, board_row):
                    result_list[pos] = str(value) if value != EMPTY else '.'
                return ''.join(result_list)
            else:
                return ''.join('.' if cell == EMPTY else str(cell) for cell in board_row)

        return ''.join(str(cell) for cell in board_row)


def parse_line(raw: str) -> Optional[List[int]]:
    line = raw.strip()

    if not line:
        return None
    if line.startswith('#') or line.startswith('%') or line.startswith('//'):
        return None
    if re.fullmatch(r'[-=+|_ ]+', line):
        return None

    # Normalize separators to handle mixed formats
    line = re.sub(r'[,|;\t]+', ' ', line)

    tokens = re.findall(r'\d+|\.+', line)
    digits: List[int] = []

    for token in tokens:
        if re.fullmatch(r'\.+', token):
            digits.extend([EMPTY] * len(token))
        elif len(token) == 1:
            digits.append(int(token))
        elif len(token) == BOARD_SIZE:
            digits.extend(int(c) for c in token)
        elif len(token) <= BOARD_SIZE and all(c.isdigit() for c in token):
            digits.extend(int(c) for c in token)
        else:
            return None

    if len(digits) != BOARD_SIZE:
        return None
    if any(d < 0 or d > BOARD_SIZE for d in digits):
        return None

    return digits


def parse_board(text: str, format_detector: FormatDetector) -> Optional[List[List[int]]]:
    valid_lines: List[List[int]] = []

    for raw in text.splitlines():
        format_type = format_detector.detect_format(raw)
        result = parse_line(raw)

        if result is not None:
            format_detector.record_line(raw, format_type)
            valid_lines.append(result)

        if len(valid_lines) == BOARD_SIZE:
            break

    if len(valid_lines) != BOARD_SIZE:
        return None

    return valid_lines


def to_prolog_term(board: List[List[int]]) -> str:
    def cell(value: int) -> str:
        return '_' if value == EMPTY else str(value)

    rows = []
    for row in board:
        cells = ",".join(cell(v) for v in row)
        rows.append(f"     [{cells}]")

    return "[\n" + ",\n".join(rows) + "\n    ]"


def solve_with_prolog(board: List[List[int]], prolog_file: str = PROLOG_SOLVER) -> Optional[List[List[int]]]:
    if not os.path.exists(prolog_file):
        print(f"ERROR: Prolog solver '{prolog_file}' not found in current directory.", file=sys.stderr)
        return None

    term = to_prolog_term(board)

    goal = (
        f"T = {term}, "
        "( sudoku(T) -> "
        "  ( forall(member(Row, T), "
        "           ( maplist([X]>>(write(X), write(' ')), Row), nl )), halt ) "
        "; write('No solution'), nl, halt )."
    )

    cmd = ["swipl", "-g", goal, "-t", "halt", prolog_file]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()
        if "No solution" in output:
            print("No solution exists for this puzzle.", file=sys.stderr)
            return None

        solved_board = []
        for line in output.split('\n'):
            if line.strip():
                numbers = [int(x) for x in line.split() if x.strip().isdigit()]
                if len(numbers) == BOARD_SIZE:
                    solved_board.append(numbers)

        if len(solved_board) == BOARD_SIZE:
            return solved_board
        else:
            print("Failed to parse Prolog output.", file=sys.stderr)
            return None

    except FileNotFoundError:
        print("ERROR: swipl not found. Please install SWI-Prolog.", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("ERROR: Solver timeout (30 seconds).", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return None


def read_from_file(filename: str) -> str:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Input file '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR reading file: {e}", file=sys.stderr)
        sys.exit(1)


def write_to_file(filename: str, content: str):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"ERROR writing to file: {e}", file=sys.stderr)
        sys.exit(1)


def interactive_input() -> str:
    print("Enter the Sudoku puzzle (9 lines).")
    print("Supported formats per line:")
    print("  • 123456789")
    print("  • 1 2 3 4 5 6 7 8 9")
    print("  • 1,2,3,4,5,6,7,8,9")
    print("  • ..3.2.6..")
    print("  • 003020600")
    print("Lines starting with # are ignored.\n")

    lines = []
    count = 0
    while count < 9:
        try:
            line = input(f"Line {count + 1}: ")
            if line.strip() and not line.startswith('#'):
                lines.append(line)
                count += 1
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            sys.exit(1)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Sudoku Solver using SWI-Prolog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--input', '-i',
                       help='Input file containing puzzle (default: interactive)')
    parser.add_argument('--output', '-o',
                       help='Output file for solution (default: stdout)')

    args = parser.parse_args()

    if args.input:
        content = read_from_file(args.input)
    else:
        content = interactive_input()

    format_detector = FormatDetector()
    board = parse_board(content, format_detector)

    if board is None:
        print("ERROR: Could not extract a valid 9x9 board.", file=sys.stderr)
        print("Make sure the input contains exactly 9 valid lines.", file=sys.stderr)
        sys.exit(1)

    print("Solving...", file=sys.stderr)
    solved_board = solve_with_prolog(board)

    if solved_board is None:
        sys.exit(1)

    output_lines = []
    for i, (board_row, original_format, original_line) in enumerate(zip(
            solved_board,
            format_detector.line_formats,
            format_detector.original_lines)):
        output_lines.append(
            format_detector.get_output_line(board_row, original_format, original_line)
        )

    output_content = '\n'.join(output_lines)

    if args.output:
        write_to_file(args.output, output_content)
        print(f"Solution written to {args.output}", file=sys.stderr)
    else:
        print(output_content)


if __name__ == "__main__":
    main()
