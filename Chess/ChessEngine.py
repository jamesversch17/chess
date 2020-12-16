"""
James Verschleiser
Engine that stores the game and determines move validity
"""


class Game:
    def __init__(self):

        # this is the gameboard that stores where the pieces and is initialized to the correct starting locations
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.turn = "w"     # who's turn it is
        self.log = []          # all the previously made moves

        self.wK_location = (7, 4)    # white king current location
        self.bK_location = (0, 4)     # black king current location

        self.enpassant = ()    # where en passant is possibleyeah

        self.castle = Castles(True, True, True, True)
        self.castle_log = [Castles(self.castle.wK, self.castle.bK, self.castle.wQ, self.castle.bQ)]

        self.checkmate = False         # is the game currently in checkmate
        self.stalemate = False          # is the game currently in stalemate

    # function that makes moves and changes where the pieces are located
    def make_move(self, move):

        self.board[move.start[0]][move.start[1]] = "--"   # set the moved piece's square to empty
        self.board[move.end[0]][move.end[1]] = move.start_sq     # put the moved piece in the final location

        self.log.append(move)    # add the move to the log
        self.switch_turns()

        # update the king's location if it was the piece moved
        if move.start_sq == 'wK':
            self.wK_location = move.end[0], move.end[1]
        if move.start_sq == 'bK':
            self.bK_location = move.end[0], move.end[1]

        # see if it is a pawn promotion
        if move.pawn_promotion:
            new_piece = move.start_sq[0] + 'Q'
            self.board[move.end[0]][move.end[1]] = new_piece

        # for en passant moves
        if move.is_en_passant:
            self.board[move.start[0]][move.end[1]] = '--'   # captured the pawn

        # if the player made a two square push with a pawn
        if move.start_sq[1] == 'P' and (move.start[0] - move.end[0] == 2 or move.start[0] - move.end[0] == -2):
            if move.start[0] == 1:
                self.enpassant = (2, move.start[1])

            elif move.start[0] == 6:
                self.enpassant = (5, move.start[1])
        else:
            self.enpassant = ()

        # if the user made a castle move
        if move.k_castle:
            self.board[move.end[0]][move.end[1] - 1] = self.board[move.end[0]][move.end[1] + 1]
            self.board[move.end[0]][move.end[1] + 1] = '--'

        elif move.q_castle:
            self.board[move.end[0]][move.end[1] + 1] = self.board[move.end[0]][move.end[1] - 2]
            self.board[move.end[0]][move.end[1] - 2] = '--'

        # update your castle rights
        self.update_castle(move)
        self.castle_log.append(Castles(self.castle.wK, self.castle.bK, self.castle.wQ, self.castle.bQ))

    # function that lets the user undo moves or allows the engine to undo the moves it looked at
    def undo_move(self):

        # if there is a move to undo
        if len(self.log) != 0:

            move = self.log.pop()       # take the last made move and then undo its effects
            self.board[move.start[0]][move.start[1]] = move.start_sq
            self.board[move.end[0]][move.end[1]] = move.end_sq
            self.switch_turns()

            # change back the king's location if the undone move was a king move
            if move.start_sq == 'wK':
                self.wK_location = move.start[0], move.start[1]
            if move.start_sq == 'bK':
                self.bK_location = move.start[0], move.start[1]

            # undo an enpassant move
            if move.is_en_passant:
                self.board[move.end[0]][move.end[1]] = '--'
                self.board[move.start[0]][move.end[1]] = move.end_sq
                self.enpassant = (move.end[0], move.end[1])

            # undo a 2 sq pawn move
            if move.start_sq[1] == 'P' and (move.start[0] - move.end[0] == 2 or move.start[0] - move.end[0] == -2):
                self.enpassant = ()

            # undo changes to castling
            self.castle_log.pop()

            # set the castle rights
            self.castle.wK = self.castle_log[-1].wK
            self.castle.bK = self.castle_log[-1].bK
            self.castle.wQ = self.castle_log[-1].wQ
            self.castle.bQ = self.castle_log[-1].bQ

            if move.k_castle:
                self.board[move.end[0]][move.end[1] + 1] = self.board[move.end[0]][move.end[1] - 1]
                self.board[move.end[0]][move.end[1] - 1] = '--'

            elif move.q_castle:
                self.board[move.end[0]][move.end[1] - 2] = self.board[move.end[0]][move.end[1] + 1]
                self.board[move.end[0]][move.end[1] + 1] = '--'

    # function that generates all the possible moves a player can make
    def all_moves(self):

        enpassant = self.enpassant      # saves current value before generating all the moves
        castle = Castles(self.castle.wK, self.castle.bK, self.castle.wQ, self.castle.bQ)

        moves = self.valid_moves()      # generate all moves that can be done by the directionality of the pieces

        if self.turn == "w":
            self.castle_moves(self.wK_location[0], self.wK_location[1], moves)
        else:
            self.castle_moves(self.bK_location[0], self.bK_location[1], moves)

        for i in range(len(moves) - 1, -1, -1):    # for each of these moves

            self.make_move(moves[i])        # make the move
            self.switch_turns()             # make_move changed turn to the opponent so now change back

            if self.in_check():          # we can't allow moves that leave the king able to be taken
                moves.remove(moves[i])

            self.switch_turns()     # switch back the turn so the opponent can move

            self.undo_move()        # undo the move

        if len(moves) == 0:             # if we can't make any moves then either checkmate or stalemate
            if self.in_check():          # it is checkmate if the king is attacked and stalemate otherwise
                self.checkmate = True
            else:
                self.stalemate = True

        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassant = enpassant
        self.castle = castle

        return moves

    # Is current player in check
    def in_check(self):

        if self.turn == "w":
            return self.square_attacked(self.wK_location[0], self.wK_location[1])
        else:
            return self.square_attacked(self.bK_location[0], self.bK_location[1])

    # Is square that we are trying to move to being attacked
    def square_attacked(self, row, col):

        self.switch_turns()   # switch and make it the opponent's turn

        opp_moves = self.valid_moves()      # calculate all of the opponent's moves

        self.switch_turns()         # back to current player's turn

        # check if any of the moves the opponent makes involves capturing the king
        for move in opp_moves:
            if move.end[0] == row and move.end[1] == col:
                return True
        return False

    # if the player makes a move that invalidates a castle move
    def update_castle(self, move):

        # white king moves
        if move.start_sq == "wK":
            self.castle.wK = False
            self.castle.wQ = False

        # black king moves
        elif move.start_sq == "bK":
            self.castle.bK = False
            self.castle.bQ = False

        # white rook moves
        elif move.start_sq == "wR":
            if move.start[0] == 7:
                if move.start[1] == 0:
                    self.castle.wQ = False
                if move.start[1] == 7:
                    self.castle.wK = False

        # black rook moves
        elif move.start_sq == "bR":
            if move.start[0] == 0:
                if move.start[1] == 0:
                    self.castle.bQ = False
                if move.start[1] == 7:
                    self.castle.bK = False

    # generates all of the moves that are possible solely based on where the pieces are able to move
    def valid_moves(self):

        moves = []

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):

                player = self.board[row][col][0]

                # if the piece's color matches the turn generate the moves based on the piece's type
                if (player == 'w' and self.turn == "w") or (player == 'b' and self.turn == 'b'):
                    piece = self.board[row][col][1]
                    if piece == 'P':
                        self.pawn_moves(row, col, moves)
                    elif piece == 'R':
                        self.rook_moves(row, col, moves)
                    elif piece == 'N':
                        self.knight_moves(row, col, moves)
                    elif piece == 'B':
                        self.bishop_moves(row, col, moves)
                    elif piece == 'Q':
                        self.queen_moves(row, col, moves)
                    elif piece == 'K':
                        self.king_moves(row, col, moves)

        return moves

    # generate all possible pawn moves
    def pawn_moves(self, row, col, moves):

        if self.turn == 'w':
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6:
                    if self.board[row - 2][col] == "--":
                        moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassant:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, en_passant=True))
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassant:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, en_passant=True))

        else:
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1:
                    if self.board[row + 2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassant:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, en_passant=True))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassant:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, en_passant=True))

    # generate all possible rook moves
    def rook_moves(self, row, col, moves):

        i = 1

        while row - 1 >= 0:
            if self.board[row - i][col][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - i, col), self.board))
                if self.board[row - i][col][0] != "-":
                    break
                i += 1
            else:
                break
        i = 1
        while row + i <= 7:
            if self.board[row + i][col][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + i, col), self.board))
                if self.board[row - i][col][0] != "-":
                    break
                i += 1
            else:
                break

        i = 1
        while col - i >= 0:
            if self.board[row][col - i][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row, col - i), self.board))
                if self.board[row][col - i][0] != "-":
                    break
                i += 1
            else:
                break
        i = 1
        while col + i <= 7:
            if self.board[row][col + i][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row, col + i), self.board))
                if self.board[row][col + i][0] != "-":
                    break
                i += 1
            else:
                break

    # generate all possible knight moves
    def knight_moves(self, row, col, moves):

        if row - 2 >= 0 and col + 1 <= 7:
            if self.board[row - 2][col + 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 2, col + 1), self.board))

        if row - 2 >= 0 and col - 1 >= 0:
            if self.board[row - 2][col - 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 2, col - 1), self.board))

        if row + 2 <= 7 and col - 1 >= 0:
            if self.board[row + 2][col - 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 2, col - 1), self.board))

        if row + 2 <= 7 and col + 1 <= 7:
            if self.board[row + 2][col + 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 2, col + 1), self.board))

        if row - 1 >= 0 and col + 2 <= 7:
            if self.board[row - 1][col + 2][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 1, col + 2), self.board))

        if row - 1 >= 0 and col - 2 >= 0:
            if self.board[row - 1][col - 2][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 1, col - 2), self.board))

        if row + 1 <= 7 and col - 2 >= 0:
            if self.board[row + 1][col - 2][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 1, col - 2), self.board))

        if row + 1 <= 7 and col + 2 <= 7:
            if self.board[row + 1][col + 2][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 1, col + 2), self.board))

    # generate all possible bishop moves
    def bishop_moves(self, row, col, moves):

        i = 1
        while 7 >= row - i >= 0 and 7 >= col - i >= 0:
            if self.board[row - i][col - i][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - i, col - i), self.board))
                if self.board[row - i][col - i][0] != "-":
                    break
                i += 1
            else:
                break

        i = 1
        while 7 >= row + i >= 0 and 7 >= col + i >= 0:
            if self.board[row + i][col + i][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + i, col + i), self.board))
                if self.board[row + i][col + i][0] != "-":
                    break
                i += 1
            else:
                break

        i = 1
        while 7 >= row + i >= 0 and 7 >= col - i >= 0:
            if self.board[row + i][col - i][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + i, col - i), self.board))
                if self.board[row + i][col - i][0] != "-":
                    break
                i += 1
            else:
                break

        i = 1
        while 7 >= row - i >= 0 and 7 >= col + i >= 0:
            if self.board[row - i][col + i][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - i, col + i), self.board))
                if self.board[row - i][col + i][0] != "-":
                    break
                i += 1
            else:
                break

    # rook can move the same as a rook and bishop combined
    def queen_moves(self, row, col, moves):

        self.rook_moves(row, col, moves)
        self.bishop_moves(row, col, moves)

    # generate the king moves
    def king_moves(self, row, col, moves):

        if row - 1 >= 0 and col + 1 <= 7:
            if self.board[row - 1][col + 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 1, col + 1), self.board))

        if row - 1 >= 0 and col - 1 >= 0:
            if self.board[row - 1][col - 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 1, col - 1), self.board))

        if row + 1 <= 7 and col - 1 >= 0:
            if self.board[row + 1][col - 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 1, col - 1), self.board))

        if row + 1 <= 7 and col + 1 <= 7:
            if self.board[row + 1][col + 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 1, col + 1), self.board))

        if row - 1 >= 0:
            if self.board[row - 1][col][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row - 1, col), self.board))

        if row + 1 <= 7:
            if self.board[row + 1][col][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row + 1, col), self.board))

        if col - 1 >= 0:
            if self.board[row][col - 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row, col - 1), self.board))

        if col + 1 <= 7:
            if self.board[row][col + 1][0] != self.board[row][col][0]:
                moves.append(Move((row, col), (row, col + 1), self.board))

    # generate possible castle moves
    def castle_moves(self, row, col, moves):
        if self.square_attacked(row, col):
            return
        if self.turn == 'w' and self.castle.wK:
            if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
                if not self.square_attacked(row, col + 1) and not self.square_attacked(row, col + 2):
                    moves.append(Move((row, col), (row, col + 2), self.board, k_castle=True))

        if self.turn == 'b' and self.castle.bK:
            if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
                if not self.square_attacked(row, col + 1) and not self.square_attacked(row, col + 2):
                    moves.append(Move((row, col), (row, col + 2), self.board, k_castle=True))

        if self.turn == 'w' and self.castle.wQ:
            if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
                if not self.square_attacked(row, col - 1) and not self.square_attacked(row, col - 2):
                    moves.append(Move((row, col), (row, col - 2), self.board, q_castle=True))

        if self.turn == 'b' and self.castle.bQ:
            if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
                if not self.square_attacked(row, col - 1) and not self.square_attacked(row, col - 2):
                    moves.append(Move((row, col), (row, col - 2), self.board, q_castle=True))

    # switch whose turn it is
    def switch_turns(self):

        if self.turn == 'w':
            self.turn = 'b'
        else:
            self.turn = 'w'


# class that stores the details of a specific move
class Move:
    def __init__(self, start, end, board, en_passant=False, k_castle=False, q_castle=False):
        self.start = start
        self.end = end
        self.start_sq = board[self.start[0]][self.start[1]]     # piece on start square
        self.end_sq = board[self.end[0]][self.end[1]]           # piece on end square

        self.pawn_promotion = False        # stores if the move involves a pawn promotion

        # sees if move is a pawn promotion
        if self.start_sq == 'wP' and self.end[0] == 0:
            self.pawn_promotion = True

        if self.start_sq == 'bP' and self.end[0] == 7:
            self.pawn_promotion = True

        self.is_en_passant = en_passant     # if the move is an en passant

        if self.is_en_passant:
            if self.start_sq == 'wP':
                self.end_sq = 'bP'
            else:
                self.end_sq = 'wP'

        self.k_castle = k_castle
        self.q_castle = q_castle

    def print_move(self):
        return self.start, self.end


# keeps track of what castles are still allowed
class Castles:
    def __init__(self, wK, bK, wQ, bQ):
        self.wK = wK
        self.bK = bK
        self.wQ = wQ
        self.bQ = bQ

