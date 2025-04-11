import sys
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

# CLI runner
def print_board(s):
    boards, macro, next_board = s
    def cell_repr(v): return {1:'X',-1:'O',0:'.'}[v]
    # print macro layout with boards
    rows = []
    for br in range(3):
        for r in range(3):
            row = []
            for bc in range(3):
                b = boards[br*3+bc]
                row.append(''.join(cell_repr(b[r*3+c]) for c in range(3)))
            rows.append(' | '.join(row))
        if br<2: rows.append('-'*11)
    print("\n".join(rows))
    print(f"Next board: {next_board if next_board is not None else 'Any'}")

def human_player(juego, s, j):
    print_board(s)
    moves = juego.jugadas_legales(s, j)
    print(f"Legal moves: {moves}")
    while True:
        inp = input(f"Player {'X' if j==1 else 'O'} move (board,cell): ")
        try:
            b,i = map(int, inp.strip().split(','))
            if (b,i) in moves:
                return (b,i)
        except:
            pass
        print("Invalid move, try again.")

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
    
    print(f"AI thinking... (player: {'X' if j==1 else 'O'})")
    move = alpha_beta_limited(juego, s, j)
    print(f"AI chose move: {move}")
    return move

def main():
    juego = UltimateTicTacToe()
    mode = sys.argv[1] if len(sys.argv)>1 else 'hva'
    if mode=='hva':
        p1, p2 = human_player, ai_player
    elif mode=='aah':
        p1, p2 = ai_player, human_player 
    else:
        p1 = p2 = ai_player
    result, final = juega_dos_jugadores(juego, p1, p2)
    print_board(final)
    print("Result:", "X wins" if result==1 else "O wins" if result==-1 else "Draw")

if __name__=='__main__':
    main()