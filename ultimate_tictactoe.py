import sys
import os
from random import shuffle
from juegos_simplificado import ModeloJuegoZT2, alpha_beta, juega_dos_jugadores

class UltimateTicTacToe(ModeloJuegoZT2):
    """
    Ultimate Tic-Tac-Toe: 9 small 3x3 boards in a 3x3 grid.
    Players: 1 (X) and -1 (O).
    State representation: 
      - boards: list of 9 lists of 9 cells (0 empty, 1 X, -1 O)
      - macro: list of 9 status (0 ongoing, 1 X won, -1 O won, 2 tie)
      - next_board: index [0..8] of small board to play, or None for any
    """
    def inicializa(self):
        boards = [[0]*9 for _ in range(9)]
        macro = [0]*9
        next_board = None
        state = (boards, macro, next_board)
        return state, 1  # X starts

    def jugadas_legales(self, s, j):
        boards, macro, next_board = s
        moves = []
        targets = [next_board] if next_board is not None and macro[next_board]==0 else [i for i in range(9) if macro[i]==0]
        for b in targets:
            for i in range(9):
                if boards[b][i]==0:
                    moves.append((b, i))
        return moves

    def transicion(self, s, a, j):
        boards, macro, _ = s
        b, i = a
        new_boards = [list(board) for board in boards]
        new_macro = list(macro)
        new_boards[b][i] = j
        # update small board status
        winner = self._check_winner(new_boards[b])
        if winner!=0:
            new_macro[b] = winner
        elif all(cell!=0 for cell in new_boards[b]):
            new_macro[b] = 2  # tie
        # determine next board
        next_board = i
        if new_macro[next_board]!=0:
            next_board = None
        return (new_boards, new_macro, next_board)

    def terminal(self, s):
        _, macro, _ = s
        # check macro winner
        if abs(self._check_winner(macro))==1:
            return True
        # tie if all small boards decided
        return all(m in (1, -1, 2) for m in macro)

    def ganancia(self, s):
        _, macro, _ = s
        w = self._check_winner(macro)
        if w==1:
            return 1
        elif w==-1:
            return -1
        else:
            return 0  # draw

    def _check_winner(self, cells):
        lines = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        for (i,j,k) in lines:
            if cells[i]==cells[j]==cells[k] and cells[i]!=0:
                return cells[i]
        return 0

# Heuristic evaluation
def heuristic(s, j):
    boards, macro, next_board = s
    score = 0
    # weight macro control
    for m in macro:
        if m==j:
            score += 100
        elif m==-j:
            score -= 100
    
    # small boards potential
    for idx, b in enumerate(boards):
        if macro[idx]==0:
            score += _small_board_potential(b, j) * 10
            score -= _small_board_potential(b, -j) * 10
    
    # strategic positions (center and corners of macro)
    strategic_indices = [0, 2, 4, 6, 8]
    for idx in strategic_indices:
        if macro[idx]==j:
            score += 50
        elif macro[idx]==-j:
            score -= 50
    
    return score

def _small_board_potential(cells, player):
    # count two-in-a-row opportunities
    lines = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    pot = 0
    for (i,j,k) in lines:
        line = [cells[i], cells[j], cells[k]]
        if line.count(player)==2 and line.count(0)==1:
            pot += 3  # two in a row with possibility to win
        elif line.count(player)==1 and line.count(0)==2:
            pot += 1  # one in a row with open spots
    return pot

# Enhanced display functions
def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board_with_colors(s):
    """Print the Ultimate Tic Tac Toe board with colors and better formatting."""
    boards, macro, next_board = s
    
    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    X_COLOR = "\033[91m"  # Bright red
    O_COLOR = "\033[94m"  # Bright blue
    HIGHLIGHT = "\033[103m"  # Yellow background
    MACRO_X = "\033[41m"  # Red background
    MACRO_O = "\033[44m"  # Blue background
    MACRO_TIE = "\033[100m"  # Grey background
    
    # Board indices for reference
    board_indices = [
        '┌───┬───┬───┐',
        '│0,0│0,1│0,2│',
        '├───┼───┼───┤',
        '│1,0│1,1│1,2│',
        '├───┼───┼───┤',
        '│2,0│2,1│2,2│',
        '└───┴───┴───┘'
    ]
    
    def cell_repr(value, is_highlight=False):
        if value == 1:
            return f"{HIGHLIGHT if is_highlight else ''}{X_COLOR}{BOLD}X{RESET}"
        elif value == -1:
            return f"{HIGHLIGHT if is_highlight else ''}{O_COLOR}{BOLD}O{RESET}"
        else:
            return f"{HIGHLIGHT if is_highlight else ''} {RESET}"
    
    def board_status(idx):
        if macro[idx] == 1:
            return f"{MACRO_X} X {RESET}"
        elif macro[idx] == -1:
            return f"{MACRO_O} O {RESET}"
        elif macro[idx] == 2:
            return f"{MACRO_TIE} # {RESET}"
        else:
            return "   "
    
    # Reference grid
    print("\nBoard reference (board,cell):")
    for line in board_indices:
        print(f"  {line}")
    
    print("\nGame state:")
    
    # Print macro status on top
    print("  Macro board:         ", end="")
    for c in range(3):
        print(board_status(c), end=" ")
    print()
    print("                       ", end="")
    for c in range(3, 6):
        print(board_status(c), end=" ")
    print()
    print("                       ", end="")
    for c in range(6, 9):
        print(board_status(c), end=" ")
    print("\n")
    
    # Print the detailed boards
    horizontal_line_small = "  ―――――――――――"
    horizontal_line_big = "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for br in range(3):
        print(horizontal_line_big)
        for r in range(3):
            for sub_r in range(1):  # Just one row per cell for compactness
                line = "  "
                for bc in range(3):
                    board_idx = br * 3 + bc
                    is_next = next_board == board_idx or (next_board is None and macro[board_idx] == 0)
                    prefix = "→ " if is_next else "  "
                    line += prefix
                    
                    for c in range(3):
                        cell_idx = r * 3 + c
                        cell_val = boards[board_idx][cell_idx]
                        is_highlight = next_board == board_idx if next_board is not None else False
                        line += cell_repr(cell_val, is_highlight)
                        line += " "
                    
                    line += "│ "
                print(line)
            
            # Cell indices inside board
            line = "  "
            for bc in range(3):
                board_idx = br * 3 + bc
                line += "  "
                for c in range(3):
                    cell_idx = r * 3 + c
                    cell_text = f"{board_idx},{cell_idx}"
                    line += f"{cell_text:3} "
                line += "│ "
            print(line)
            
            # Separator after each row in the small board
            if r < 2:
                line = "  "
                for bc in range(3):
                    line += "  " + horizontal_line_small + " │ "
                print(line)
        
        # Separator between big board rows
        if br < 2:
            print(horizontal_line_big)
    
    print(horizontal_line_big)
    
    # Print next board info
    if next_board is not None:
        print(f"\nNext move must be in board {next_board} (row {next_board//3}, col {next_board%3})")
    else:
        print("\nNext move can be in any open board")

# CLI runner functions
def human_player(juego, s, j):
    clear_screen()
    print_board_with_colors(s)
    moves = juego.jugadas_legales(s, j)
    
    # Format moves for better readability
    formatted_moves = []
    for b, i in moves:
        row, col = i // 3, i % 3
        formatted_moves.append(f"({b},{i}) [board {b}, position ({row},{col})]")
    
    print(f"\nPlayer {'X' if j==1 else 'O'}'s turn")
    
    while True:
        inp = input(f"\nEnter your move (board,cell): ")
        try:
            b, i = map(int, inp.strip().split(','))
            if (b, i) in moves:
                return (b, i)
            else:
                print(f"Invalid move. The move ({b},{i}) is not legal.")
        except ValueError:
            print("Invalid format. Please use 'board,cell' format (e.g. '4,8').")

def ai_player(juego, s, j):
    # Add a maximum depth to limit search
    MAX_DEPTH = 3
    
    def evaluate_move(state, player):
        return heuristic(state, player)
    
    def alpha_beta_limited(juego, estado, jugador, depth=MAX_DEPTH):
        """Limited depth alpha-beta with move ordering"""
        j = jugador
        
        def max_val(estado, jugador, alpha, beta, depth):
            if juego.terminal(estado) or depth == 0:
                return evaluate_move(estado, j)
            v = -float('inf')
            jugadas = list(juego.jugadas_legales(estado, jugador))
            # Order moves by simple heuristic
            scored_moves = []
            for a in jugadas:
                next_state = juego.transicion(estado, a, jugador)
                scored_moves.append((evaluate_move(next_state, j), a))
            scored_moves.sort(reverse=True)
            
            for _, a in scored_moves:
                v = max(v, min_val(juego.transicion(estado, a, jugador), -jugador, alpha, beta, depth-1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v
        
        def min_val(estado, jugador, alpha, beta, depth):
            if juego.terminal(estado) or depth == 0:
                return evaluate_move(estado, j)
            v = float('inf')
            jugadas = list(juego.jugadas_legales(estado, jugador))
            # Order moves by simple heuristic
            scored_moves = []
            for a in jugadas:
                next_state = juego.transicion(estado, a, jugador)
                scored_moves.append((evaluate_move(next_state, j), a))
            scored_moves.sort()  # Ascending for minimizer
            
            for _, a in scored_moves:
                v = min(v, max_val(juego.transicion(estado, a, jugador), -jugador, alpha, beta, depth-1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v
        
        # Find best move with alpha-beta
        best_score = -float('inf')
        best_move = None
        jugadas = list(juego.jugadas_legales(estado, jugador))
        
        # Pre-evaluate and sort moves for better pruning
        scored_moves = []
        for a in jugadas:
            next_state = juego.transicion(estado, a, jugador)
            scored_moves.append((evaluate_move(next_state, j), a))
        scored_moves.sort(reverse=True)
        
        alpha = -float('inf')
        beta = float('inf')
        
        for score, a in scored_moves:
            v = min_val(juego.transicion(estado, a, jugador), -jugador, alpha, beta, depth-1)
            if v > best_score:
                best_score = v
                best_move = a
            alpha = max(alpha, best_score)
        
        return best_move
    
    clear_screen()
    print_board_with_colors(s)
    print(f"\nAI ({('X' if j==1 else 'O')}) is thinking...")
    
    move = alpha_beta_limited(juego, s, j)
    b, i = move
    row, col = i // 3, i % 3
    print(f"AI chose: ({b},{i}) [board {b}, position ({row},{col})]")
    
    # Pause briefly so humans can see the AI's move
    input("\nPress Enter to continue...")
    return move

def main():
    juego = UltimateTicTacToe()
    
    clear_screen()
    print("\n" + "=" * 60)
    print("  ULTIMATE TIC TAC TOE")
    print("=" * 60)
    print("\nRules:")
    print("1. The board consists of 9 small tic-tac-toe boards arranged in a 3x3 grid")
    print("2. Each turn, you must play in the small board indicated by the previous move")
    print("3. Win three small boards in a row to win the game")
    print("\nGame modes:")
    print(" hva - Human vs AI (default)")
    print(" aah - AI vs Human")
    print(" ava - AI vs AI")
    print("\n" + "=" * 60)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'hva'
    
    if mode == 'hva':
        p1, p2 = human_player, ai_player
        print("\nYou're playing as X (first)")
    elif mode == 'aah':
        p1, p2 = ai_player, human_player
        print("\nYou're playing as O (second)")
    else:
        p1 = p2 = ai_player
        print("\nAI vs AI demonstration")
    
    input("\nPress Enter to start the game...")
    
    result, final = juega_dos_jugadores(juego, p1, p2)
    
    clear_screen()
    print("\n" + "=" * 60)
    print("  GAME OVER")
    print("=" * 60 + "\n")
    
    print_board_with_colors(final)
    
    if result == 1:
        print("\nResult: X WINS!")
    elif result == -1:
        print("\nResult: O WINS!")
    else:
        print("\nResult: DRAW")
        
    print("\nThanks for playing Ultimate Tic Tac Toe!")
    print("=" * 60)

if __name__ == '__main__':
    main()