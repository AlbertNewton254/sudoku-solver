/** solver.pl
 *
 * Sudoku 9x9 Solver in Prolog
 * Logic Applied to Computing - Final Project
 * Federal University of Paraíba (UFPB)
 * Computer Science Bachelor's Degree
 *
 * Student: Miguel Mochizuki Silva
 * Registration: 20250071451
 *
 * Concepts demonstrated:
 * - Facts and rules
 * - Recursion
 * - Backtracking
 * - Unification
 * - Lists
 * - Constraint Logic Programming (CLPFD)
 */

:- use_module(library(clpfd)).
:- use_module(library(lists)).

% =============================================================================
% MAIN PREDICATE
% =============================================================================

sudoku(Board) :-
    length(Board, 9),
    maplist(length_(9), Board),
    append(Board, Vars),
    Vars ins 1..9,
    valid_rows(Board),
    valid_columns(Board),
    valid_regions(Board),
    labeling([ff], Vars).

length_(N, L) :- length(L, N).

% =============================================================================
% ROW VALIDATION
% =============================================================================

valid_rows([]).
valid_rows([Row|Rest]) :-
    all_distinct(Row),
    valid_rows(Rest).

% =============================================================================
% COLUMN VALIDATION
% =============================================================================

valid_columns(Board) :-
    transpose(Board, Columns),
    valid_rows(Columns).

% =============================================================================
% REGION VALIDATION (3x3 blocks)
% =============================================================================

valid_regions(Board) :-
    Board = [R1,R2,R3,R4,R5,R6,R7,R8,R9],
    regions(R1,R2,R3),
    regions(R4,R5,R6),
    regions(R7,R8,R9).

regions([], [], []).
regions([A1,A2,A3|Rest1],
        [B1,B2,B3|Rest2],
        [C1,C2,C3|Rest3]) :-
    all_distinct([A1,A2,A3,B1,B2,B3,C1,C2,C3]),
    regions(Rest1, Rest2, Rest3).

% =============================================================================
% DISPLAY PREDICATES
% =============================================================================

separator :-
    write('  - - - - - - - - -'), nl.

cell(C) :- var(C), !, write('·').
cell(C) :- write(C).

display_row(Row) :-
    Row = [A,B,C,D,E,F,G,H,I],
    write('  '),
    cell(A), write(' '), cell(B), write(' '), cell(C),
    write('   '),
    cell(D), write(' '), cell(E), write(' '), cell(F),
    write('   '),
    cell(G), write(' '), cell(H), write(' '), cell(I),
    nl.

display_board(Board) :-
    Board = [R1,R2,R3,R4,R5,R6,R7,R8,R9],
    nl,
    display_row(R1),
    display_row(R2),
    display_row(R3),
    separator,
    display_row(R4),
    display_row(R5),
    display_row(R6),
    separator,
    display_row(R7),
    display_row(R8),
    display_row(R9),
    nl.

% =============================================================================
% EXAMPLE PUZZLES
% =============================================================================

puzzle(easy,
    [[_,_,3, _,2,_, 6,_,_],
     [9,_,_, 3,_,5, _,_,1],
     [_,_,1, 8,_,6, 4,_,_],

     [_,_,8, 1,_,2, 9,_,_],
     [7,_,_, _,_,_, _,_,8],
     [_,_,6, 7,_,8, 2,_,_],

     [_,_,2, 6,_,9, 5,_,_],
     [8,_,_, 2,_,3, _,_,9],
     [_,_,5, _,1,_, 3,_,_]]).

puzzle(medium,
    [[_,_,_, 2,6,_, 7,_,1],
     [6,8,_, _,7,_, _,9,_],
     [1,9,_, _,_,4, 5,_,_],

     [8,2,_, 1,_,_, _,4,_],
     [_,_,4, 6,_,2, 9,_,_],
     [_,5,_, _,_,3, _,2,8],

     [_,_,9, 3,_,_, _,7,4],
     [_,4,_, _,5,_, _,3,6],
     [7,_,3, _,1,8, _,_,_]]).

puzzle(hard,
    [[_,_,_, _,_,_, _,_,_],
     [_,_,_, _,_,3, _,8,5],
     [_,_,1, _,2,_, _,_,_],

     [_,_,_, 5,_,7, _,_,_],
     [_,_,4, _,_,_, 1,_,_],
     [_,9,_, _,_,_, _,_,_],

     [5,_,_, _,_,_, _,7,3],
     [_,_,2, _,1,_, _,_,_],
     [_,_,_, _,4,_, _,_,9]]).

list_puzzles :-
    write('  1. easy'), nl,
    write('  2. medium'), nl,
    write('  3. hard'), nl,
    write('  4. manual input'), nl.

puzzle_name(1, easy).
puzzle_name(2, medium).
puzzle_name(3, hard).

% =============================================================================
% MANUAL BOARD INPUT
% =============================================================================

read_row(Row) :-
    write('  Enter 9 numbers separated by spaces (0 = empty): '),
    read_term(Row, []).

replace_zeros([], []).
replace_zeros([0|T], [_|T2]) :- replace_zeros(T, T2).
replace_zeros([H|T], [H|T2]) :- H \= 0, replace_zeros(T, T2).

read_board(Board) :-
    nl,
    write('Enter the board row by row.'), nl,
    write('Format: [5,3,0,0,7,0,0,0,0] (0 = empty)'), nl, nl,
    numlist(1, 9, Nums),
    maplist(read_row_numbered, Nums, RawRows),
    maplist(replace_zeros, RawRows, Board).

read_row_numbered(N, Row) :-
    format('  Row ~w: ', [N]),
    read_term(Row, []).

% =============================================================================
% TIMER
% =============================================================================

solve_with_time(Board, Time) :-
    get_time(Start),
    (sudoku(Board) -> true ; fail),
    get_time(End),
    Time is End - Start.

% =============================================================================
% MAIN CLI FLOW
% =============================================================================

main :-
    header,
    menu_loop,
    write('Goodbye.'), nl.

header :-
    nl,
    write('Sudoku 9x9 -- Logic Applied to Computing'), nl,
    write('Miguel Mochizuki Silva / 20250071451'), nl.

menu_loop :-
    nl,
    write('What would you like to do?'), nl,
    write('  1. solve an example puzzle'), nl,
    write('  2. enter a puzzle manually'), nl,
    write('  3. about'), nl,
    write('  0. exit'), nl,
    nl,
    write('> '),
    read_term(Option, []),
    nl,
    process_option(Option).

process_option(0) :- !.
process_option(1) :- !, select_puzzle, menu_loop.
process_option(2) :- !, solve_manual,  menu_loop.
process_option(3) :- !, about,         menu_loop.
process_option(_) :-
    write('Invalid option.'), nl,
    menu_loop.

% -------- option 1: example puzzles --------

select_puzzle :-
    nl,
    write('Which puzzle?'), nl,
    list_puzzles,
    nl,
    write('> '),
    read_term(Choice, []),
    nl,
    (   Choice =:= 4
    ->  solve_manual
    ;   puzzle_name(Choice, Name)
    ->  puzzle(Name, Board),
        solve_and_display(Name, Board)
    ;   write('Invalid option.'), nl
    ).

solve_and_display(Name, Board) :-
    format('Puzzle: ~w~n', [Name]),
    write('Initial:'),
    display_board(Board),
    (   solve_with_time(Board, Time)
    ->  write('Solution:'),
        display_board(Board),
        format('Time: ~4f s~n', [Time])
    ;   write('No solution found.'), nl
    ).

% -------- option 2: manual --------

solve_manual :-
    read_board(Board),
    solve_and_display(manual, Board).

% -------- option 3: about --------

about :-
    nl,
    write('Sudoku 9x9 solver in Prolog'), nl,
    write('Uses CLP(FD) constraints'), nl,
    nl,
    write('Course     : Logic Applied to Computing'), nl,
    write('Program    : Computer Science / UFPB'), nl,
    write('Student    : Miguel Mochizuki Silva'), nl,
    write('Registration: 20250071451'), nl.

% =============================================================================
% PROGRAMMATIC INTERFACE FOR EXTERNAL CALLS
% =============================================================================

% solve_and_print(+Board)
% Accepts a 9x9 board (with variables for empty cells) and prints the solution.
% Each row is printed on a single line in the format: [1,2,3,4,5,6,7,8,9]
% Usage: swipl -q -g "solve_and_print(Board)" -t halt solver.pl
solve_and_print(Board) :-
    (   sudoku(Board)
    ->  maplist(writeln, Board)
    ;   write('ERROR: No solution found'), nl,
        halt(1)
    ).

% =============================================================================
% AUTO ENTRY POINT (for interactive CLI usage)
% =============================================================================

% To run the interactive CLI, use:
%   swipl -q -g main -t halt solver.pl
%
% The automatic initialization is commented out to allow programmatic usage
% from external programs (like app.py) without interference.
%
% :- initialization(main, main).