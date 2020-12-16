"""
James Verschleiser
Minimax algorithm for my Chess game
"""


class AI:

    def __init__(self, game):
        self.game = game

        # values of the various pieces
        self.values = {"wP": 10, "bP": -10, "wB": 30, "bB": -30, "wN": 30, "bN": -30, "wR": 50, "bR": -50, \
                       "wQ": 90, "bQ": -90, "wK": 900, "bK": -900}

    # function to find the best move available
    def find_move(self, depth, maximize):
        moves = self.game.all_moves()      # generate all valid moves

        # if there are no moves then the game must be over
        if len(moves) == 0:
            self.game.checkmate = True
            return None

        best_move = -9999       # score of the best move
        final_move = None

        for move in moves:  # for each possible move

            self.game.make_move(move)   # make the move
            score = max(best_move, self.minimax(depth - 1, not maximize))
            self.game.undo_move()       # undo made move

            if score > best_move:       # if the board is better now than before the move was made
                best_move = score
                final_move = move

        return final_move

    # helper function to find best move
    def minimax(self, depth, maximize, alpha=-50000, beta=50000):

        # if this is the last move before returning
        if depth == 0:
            return -self.score()

        # calculate the next set of moves
        moves = self.game.all_moves()

        # depending on whose turn it is
        if maximize:

            best_move = -9999

            for move in moves:

                self.game.make_move(move)
                best_move = max(best_move, self.minimax(depth - 1, not maximize, alpha, beta)) # go forward another move
                self.game.undo_move()
                alpha = max(alpha, best_move)

                if beta <= alpha:       # eliminates tracks that won't work
                    return best_move

            return best_move

        else:

            best_move = 9999

            for move in moves:

                self.game.make_move(move)
                best_move = min(best_move, self.minimax(depth - 1, not maximize, alpha, beta))
                self.game.undo_move()
                beta = min(beta, best_move)        # eliminates tracks that won't work

                if beta <= alpha:
                    return best_move

            return best_move

    # method to evaluate the current position
    def score(self):

        score = 0

        # for each square
        for row in range(8):
            for col in range(8):
                if self.game.board[row][col] != '--':
                    score += self.values[self.game.board[row][col]]     # if there is a piece add its value
                    
        return score
