import pandas as pd
import numpy as np
import sys

#create board
board = pd.DataFrame([['A1', 'B1', 'C1'],
                   ['A2', 'B2', 'C2'],
                   ['A3', 'B3', 'C3']],
                   columns=['A', 'B', 'C'])

#create set of valid moves
valid_moves = set(board.values.flatten())
move_history = []

#create f() for checking if anyone has won yet
def check_win(board, marker):
    board_array = board.to_numpy()
    #check rows then columns then diagonals for single marker
    return (
        any(np.all(row == marker) for row in board_array) or
        any(np.all(board_array[:, col] == marker) for col in range(3)) or
        np.all(np.diag(board_array) == marker) or
        np.all(np.diag(np.fliplr(board_array)) == marker)
    )

for i in range(9):
    print(board.to_string(index=False, header=False))
    #order of play
    if i % 2 == 0:
        player, marker = "Player 1 (X)", 'X'
    else:
        player, marker = "Player 2 (O)", 'O'

    #input from players
    while True:
        pick = input(f'Make Your Move {player}: ').upper()
        if (pick not in valid_moves) or (pick in move_history):
            print("Invalid move! Move not in valid moves.")
        elif pick in move_history:
            print("Invalid move! Move already made.")
        else:
            move_history.append(pick)
            break
    
    #update board
    board.replace(pick, marker, inplace=True)

    #win condition
    if check_win(board, marker):
        print(board.to_string(index=False, header=False))
        print(f"{player} wins!".upper())
        sys.exit()

#draw condition
else:
    print(board.to_string(index=False, header=False))
    print("DRAW!")