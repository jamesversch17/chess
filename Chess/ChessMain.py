"""
James Verschleiser
This is the driver file for my  chess game.
"""

import pygame as p
from Chess import ChessEngine
from Chess import ChessAI

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

menu = True
multiplayer = False
single = False


# load in the chess piece images
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.image.load("images/" + piece + ".png")


# the function that actually runs the game
def main():
    global menu, multiplayer, single

    # standard pygame initialization
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    g = ChessEngine.Game()      # create the game
    AI = ChessAI.AI(g)          # start the AI
    valid_moves = g.all_moves()         # generate all the initial moves that can be made
    find_moves = False

    load_images()

    running = True
    curr_sq = ()
    clicks = []

    while running:

        for e in p.event.get():

            # allows the user to quit the program
            if e.type == p.QUIT:
                running = False

            # if the event is the user clicking the mouse
            elif e.type == p.MOUSEBUTTONDOWN:

                location = p.mouse.get_pos()  # location of the mouse click

                # buttons on the menu that allow players to choose game mode
                if menu:
                    if WIDTH // 4 <= location[0] <= (WIDTH // 4) + (SQ_SIZE * 4):
                        if 2 * (HEIGHT // 4) <= location[1] <= 2 * (HEIGHT // 4) + SQ_SIZE:
                            menu = False
                            single = True

                    if WIDTH // 4 <= location[0] <= (WIDTH // 4) + (SQ_SIZE * 4):
                        if 3 * (HEIGHT // 4) <= location[1] <= 3 * (HEIGHT // 4) + SQ_SIZE:
                            menu = False
                            multiplayer = True
                    continue    # make sure you don't move pieces while on menu screen

                # finding the square coordinates of the mouseclick
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE

                # if they double clicked on the same square then reset
                if curr_sq == (row, col):
                    curr_sq = ()
                    clicks = []

                else:
                    curr_sq = (row, col)
                    clicks.append(curr_sq)

                if len(clicks) == 2:   # if there are two loaded clicks(piece they want to move, where to move)

                    if multiplayer:
                        move = ChessEngine.Move(clicks[0], clicks[1], g.board)   # store the move

                        for i in range(len(valid_moves)):
                            # if the move stored is valid given the rules of chess
                            if valid_moves[i].print_move() == move.print_move():
                                g.make_move(valid_moves[i])     # make the move
                                find_moves = True    # tell the computer to begin calculating the opponent's valid moves
                                curr_sq = ()
                                clicks = []

                        if curr_sq != ():
                            clicks = [curr_sq]

                    # for single player games against the computer
                    if single:
                        move = ChessEngine.Move(clicks[0], clicks[1], g.board)  # store the move

                        for i in range(len(valid_moves)):
                            # if the move stored is valid given the rules of chess
                            if move is not None:
                                if valid_moves[i].print_move() == move.print_move():
                                    g.make_move(valid_moves[i])  # make the move
                                    find_moves = True  # tell the computer to begin calculating the player's valid moves

                                    move = AI.find_move(2, True)       # finds the best move
                                    if move is not None:       # makes sure there is a move (not checkmate or stalemate)
                                        g.make_move(move)

                                    curr_sq = ()
                                    clicks = []

                        # adds the selected square to clicks
                        if curr_sq != ():
                            clicks = [curr_sq]

                # if the game is over go back to menu and reset the game
                if g.checkmate or g.stalemate:
                    menu = True
                    single = False
                    multiplayer = False
                    g = ChessEngine.Game()
                    AI = ChessAI.AI(g)
                    find_moves = True

            elif e.type == p.KEYDOWN:

                # if the user clicks u then we want to undo the last made move
                if e.key == p.K_u:
                    g.undo_move()
                    find_moves = True

        if find_moves:      # this calculates all the possible next moves

            valid_moves = g.all_moves()
            find_moves = False

        # if a game is ongoing then draw the board
        if single or multiplayer:
            draw_board(screen, g)

        # draw the menu
        if menu:
            draw_menu(screen)

        clock.tick(MAX_FPS)
        p.display.flip()


# function that draws the menu screen
def draw_menu(screen):
    # create the font for the title
    title_font = p.font.SysFont('Corbel', 50)
    title = title_font.render('Welcome to my Chess Game', True, p.Color("gray"))

    # create the font for the buttons
    button_font = p.font.SysFont('Corbel', 42)
    button1 = button_font.render('Single Player', True, p.Color("white"))
    button2 = button_font.render('Multiplayer', True, p.Color("white"))

    # draw the title
    screen.fill(p.Color("white"))
    screen.blit(title, (WIDTH // 20, HEIGHT // 4))

    # draw the buttons
    p.draw.rect(screen, p.Color("gray"), p.Rect(WIDTH // 4, 2 * (HEIGHT // 4), SQ_SIZE * 4, SQ_SIZE))
    screen.blit(button1, (WIDTH // 4, 2 * (HEIGHT // 4)))
    p.draw.rect(screen, p.Color("gray"), p.Rect(WIDTH // 4, 3 * (HEIGHT // 4), SQ_SIZE * 4, SQ_SIZE))
    screen.blit(button2, (WIDTH // 4, 3 * (HEIGHT // 4)))


# draws the board by adding the squares and pieces
def draw_board(screen, g):

    white = p.Color("white")
    gray = p.Color("gray")

    # draws the squares in the famous checkerboard pattern
    for row in range(DIMENSION):
        for col in range(DIMENSION):

            if row % 2 == 0:
                if col % 2 == 0:
                    p.draw.rect(screen, white, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    p.draw.rect(screen, gray, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            else:
                if col % 2 == 0:
                    p.draw.rect(screen, gray, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    p.draw.rect(screen, white, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    # responsible for adding the pieces to the correct squares
    for row in range(DIMENSION):
        for col in range(DIMENSION):

            square = g.board[row][col]

            if square != "--":    # if the square is supposed to have a piece on it
                screen.blit(IMAGES[square], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


main()
