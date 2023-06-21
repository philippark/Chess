import pygame
import ChessEngine

WIDTH = HEIGHT = 400
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Pack the dictionary of images
"""
def load_images():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']

    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
Handles user input and updating the graphics
"""
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False

    load_images()
    running = True

    sqSelected = ()
    playerClicks = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    loc = pygame.mouse.get_pos()
                    col = loc[0] // SQ_SIZE
                    row = loc[1] // SQ_SIZE

                    #if clicked on same square, deselect
                    if sqSelected == (row, col): 
                        sqSelected = ()
                        playerClicks = []   
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                        
                    #if a move was made, check if valid, then make move if valid
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif event.type == pygame.KEYDOWN:
                #undo 
                if event.key == pygame.K_u:
                    gs.undoMove()
                    moveMade = True
                    animate = False

                #reset board
                if event.key == pygame.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

                     

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        
        if len(gs.moveLog) != 0:
            drawGameState(screen, gs, validMoves, sqSelected, gs.moveLog[-1])
        else:
            drawGameState(screen, gs, validMoves, sqSelected, ChessEngine.Move((-1,-1), (-1,-1), gs.board))

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black Won!")
            else:
                drawText(screen, "White Won!")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Draw")
         
        
        clock.tick(MAX_FPS)
        
        pygame.display.flip()


"""
Highlights move squares
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):

            #selected square
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color("yellow"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            radius = 8
            emptySquare = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(emptySquare, (0, 0, 0, 30), (radius, radius), radius)

            capture_radius = 25
            captureSquare = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(captureSquare, (0, 0, 0, 30), (capture_radius, capture_radius), capture_radius)


            #moves
            s.fill(pygame.Color("black"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if gs.board[move.endRow][move.endCol] == "--":
                        screen.blit(emptySquare, (move.endCol*SQ_SIZE + SQ_SIZE//2 - radius, move.endRow*SQ_SIZE + SQ_SIZE//2 - radius))
                    else:
                        screen.blit(captureSquare, (move.endCol*SQ_SIZE + SQ_SIZE//2 - capture_radius, move.endRow*SQ_SIZE + SQ_SIZE//2 - capture_radius))


def highlightMove(screen, move):
    s = pygame.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(pygame.Color("yellow"))
    if move.startRow != -1:
        screen.blit(s, (move.startCol*SQ_SIZE, move.startRow*SQ_SIZE))
        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


    
"""
Draws the game graphics on the screen
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveMade):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    highlightMove(screen, moveMade)
    drawPieces(screen, gs.board)



def drawBoard(screen):
    global colors
    colors = [pygame.Color("white"), pygame.Color("grey")]
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if (piece != "--"):
                screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = ( abs(dR) + abs(dC) )* framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        #erase piece from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSquare)

        #put captured piece back into original square
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        #draw moving piece
        highlightMove(screen, move)
        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(100)


def drawText(screen, text):
    font = pygame.font.SysFont("Helvitica", 32, True, False)
    textObject = font.render(text, 0, pygame.Color("Black"))
    textLocation = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)

    box_width = 200
    box_height = 150
    textBox = pygame.Surface((box_width, box_height))
    textBox.fill(pygame.Color("white"))
    screen.blit(textBox, (WIDTH//2 - box_width//2, HEIGHT//2 - box_height//2))

    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()
