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

    load_images()
    running = True

    sqSelected = ()
    playerClicks = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                    
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())

                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                    
                    if not moveMade:
                        playerClicks = [sqSelected]

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        
        pygame.display.flip()
    
"""
Draws the game graphics on the screen
"""
def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)



def drawBoard(screen):
    #light = (234, 235, 200)
    #dark = (119,154,88)

    light = pygame.Color("white")
    dark = pygame.Color("grey")
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if (r + c) % 2 == 0:
                pygame.draw.rect(screen, dark, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            else:
                pygame.draw.rect(screen, light, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if (piece != "--"):
                screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



if __name__ == "__main__":
    main()
