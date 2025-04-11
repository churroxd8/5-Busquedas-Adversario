import sys
from random import shuffle
from juegos_simplificado import ModeloJuegoZT2, alpha_beta, juega_dos_jugadores

class UltimateTicTacToe(ModeloJuegoZT2):
    """
    Ultimate Tic-Tac-Toe: 9 tableros pequeños de 3x3 en una cuadrícula de 3x3.
    Jugadores: 1 (X) y -1 (O).
    Representación del estado: 
      - boards: lista de 9 listas de 9 celdas (0 vacío, 1 X, -1 O)
      - macro: lista de 9 estados (0 en curso, 1 X ganó, -1 O ganó, 2 empate)
      - next_board: índice [0..8] del tablero pequeño a jugar, o None para cualquiera
    """
    def inicializa(self):
        boards = [[0]*9 for _ in range(9)]
        macro = [0]*9
        next_board = None
        state = (boards, macro, next_board)
        return state, 1  # X comienza

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
        # actualizar estado del tablero pequeño
        winner = self._check_winner(new_boards[b])
        if winner!=0:
            new_macro[b] = winner
        elif all(cell!=0 for cell in new_boards[b]):
            new_macro[b] = 2  # empate
        # determinar siguiente tablero
        next_board = i
        if new_macro[next_board]!=0:
            next_board = None
        return (new_boards, new_macro, next_board)

    def terminal(self, s):
        _, macro, _ = s
        # verificar ganador macro
        if abs(self._check_winner(macro))==1:
            return True
        # empate si todos los tableros pequeños están decididos
        return all(m in (1, -1, 2) for m in macro)

    def ganancia(self, s):
        _, macro, _ = s
        w = self._check_winner(macro)
        if w==1:
            return 1
        elif w==-1:
            return -1
        else:
            return 0  # empate

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

# Evaluación heurística
def heuristic(s, j):
    boards, macro, next_board = s
    score = 0
    # peso del control macro
    for m in macro:
        if m==j:
            score += 100
        elif m==-j:
            score -= 100
    
    # potencial de tableros pequeños
    for idx, b in enumerate(boards):
        if macro[idx]==0:
            score += _small_board_potential(b, j) * 10
            score -= _small_board_potential(b, -j) * 10
    
    # posiciones estratégicas
    strategic_indices = [0, 2, 4, 6, 8]
    for idx in strategic_indices:
        if macro[idx]==j:
            score += 50
        elif macro[idx]==-j:
            score -= 50
    
    return score

def _small_board_potential(cells, player):
    # contar oportunidades de dos en línea
    lines = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    pot = 0
    for (i,j,k) in lines:
        line = [cells[i], cells[j], cells[k]]
        if line.count(player)==2 and line.count(0)==1:
            pot += 3  # dos en línea con posibilidad de ganar
        elif line.count(player)==1 and line.count(0)==2:
            pot += 1  # uno en línea con espacios abiertos
    return pot

# Función de visualización mejorada simple
def print_board(s):
    boards, macro, next_board = s
    
    def cell_repr(v):
        return {1:'X', -1:'O', 0:'.'}[v]
    
    def board_status(idx):
        if macro[idx] == 1:
            return "[X]"
        elif macro[idx] == -1:
            return "[O]"
        elif macro[idx] == 2:
            return "[=]"  # empate
        else:
            return "   "
    
    # Imprimir referencia del tablero
    print("\nReferencia del tablero:")
    print("┌───┬───┬───┐")
    print("│0,1│0,2│0,3│")
    print("├───┼───┼───┤")
    print("│1,0│1,1│1,2│")
    print("├───┼───┼───┤")
    print("│2,0│2,1│2,2│")
    print("└───┴───┴───┘")
    
    # Imprimir estado del tablero macro
    print("\nTablero macro:")
    for r in range(3):
        status_row = " ".join(board_status(r*3+c) for c in range(3))
        print(status_row)
    
    # Imprimir tablero principal
    print("\nTablero de juego:")
    for br in range(3):
        for r in range(3):
            row_parts = []
            for bc in range(3):
                b = br*3+bc
                row = ""
                # Marcar tablero activo con asteriscos
                if next_board == b or (next_board is None and macro[b] == 0):
                    row += "*"
                else:
                    row += " "
                # Imprimir celdas en esta fila de este tablero
                row += "".join(cell_repr(boards[b][r*3+c]) for c in range(3))
                row_parts.append(row)
            print(" | ".join(row_parts))
        if br < 2:
            print("-" * 17)  # Separador entre filas macro
    
    # Imprimir información del siguiente tablero
    if next_board is not None:
        print(f"\nEl siguiente movimiento debe ser en el tablero {next_board}")
    else:
        print("\nEl siguiente movimiento puede ser en cualquier tablero abierto")

def human_player(juego, s, j):
    print_board(s)
    moves = juego.jugadas_legales(s, j)
    print(f"\nTurno del jugador {'X' if j==1 else 'O'}")
    print(f"Movimientos legales: {moves}")
    
    while True:
        inp = input(f"Introduce tu movimiento (tablero,celda): ")
        try:
            b, i = map(int, inp.strip().split(','))
            if (b, i) in moves:
                return (b, i)
            else:
                print(f"Movimiento inválido. Inténtalo de nuevo.")
        except:
            print("Formato inválido. Usa 'tablero,celda' (ej. '4,8').")

def ai_player(juego, s, j):
    # Profundidad máxima para la búsqueda alpha-beta
    MAX_DEPTH = 3
    
    def evaluate_move(state, player):
        return heuristic(state, player)
    
    def alpha_beta_limited(juego, estado, jugador, depth=MAX_DEPTH):
        """Alpha-beta de profundidad limitada con ordenación de movimientos"""
        j = jugador
        
        def max_val(estado, jugador, alpha, beta, depth):
            if juego.terminal(estado) or depth == 0:
                return evaluate_move(estado, j)
            v = -float('inf')
            jugadas = list(juego.jugadas_legales(estado, jugador))
            # Ordenar movimientos por heurística simple
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
            # Ordenar movimientos por heurística simple
            scored_moves = []
            for a in jugadas:
                next_state = juego.transicion(estado, a, jugador)
                scored_moves.append((evaluate_move(next_state, j), a))
            scored_moves.sort()  # Ascendente para minimizador
            
            for _, a in scored_moves:
                v = min(v, max_val(juego.transicion(estado, a, jugador), -jugador, alpha, beta, depth-1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v
        
        # Encontrar mejor movimiento con alpha-beta
        best_score = -float('inf')
        best_move = None
        jugadas = list(juego.jugadas_legales(estado, jugador))
        
        # Pre-evaluar y ordenar movimientos para mejor poda
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
    
    print(f"\nLa IA ({('X' if j==1 else 'O')}) está pensando...")
    move = alpha_beta_limited(juego, s, j)
    print(f"La IA eligió el movimiento: {move}")
    return move

def main():
    juego = UltimateTicTacToe()
    
    print("\n==== ULTIMATE TIC TAC TOE ====")
    print("\nReglas:")
    print("1. En cada turno, juega en el tablero pequeño indicado por el movimiento anterior")
    print("2. Gana tres tableros pequeños en línea para ganar el juego")
    print("\nModos de juego:")
    print("  hva - Humano vs IA (predeterminado)")
    print("  aah - IA vs Humano")
    print("  ava - IA vs IA")
    
    # Procesar argumento de línea de comandos
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Si no se proporciona modo, preguntar al usuario
    if mode not in ['hva', 'aah', 'ava']:
        print("\nSelecciona el modo de juego:")
        print("1. Humano vs IA (tú juegas primero)")
        print("2. IA vs Humano (la IA juega primero)")
        print("3. IA vs IA (demostración)")
        choice = input("Introduce tu elección (1-3): ")
        
        if choice == '1':
            mode = 'hva'
        elif choice == '2':
            mode = 'aah'
        elif choice == '3':
            mode = 'ava'
        else:
            print("Elección inválida. Usando Humano vs IA por defecto.")
            mode = 'hva'
    
    # Establecer jugadores según el modo
    if mode == 'hva':
        p1, p2 = human_player, ai_player
        print("\nJuegas como X (primero)")
    elif mode == 'aah':
        p1, p2 = ai_player, human_player
        print("\nJuegas como O (segundo)")
    else:  # ava
        p1 = p2 = ai_player
        print("\nDemostración IA vs IA")
    
    # Jugar el juego
    result, final = juega_dos_jugadores(juego, p1, p2)
    
    # Mostrar estado final
    print("\n==== FIN DEL JUEGO ====")
    print_board(final)
    
    if result == 1:
        print("\nResultado: ¡X GANA!")
    elif result == -1:
        print("\nResultado: ¡O GANA!")
    else:
        print("\nResultado: EMPATE")
        
    print("\n¡Gracias por jugar!")

if __name__ == '__main__':
    main()