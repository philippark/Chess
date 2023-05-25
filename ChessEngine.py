"""
Handles all the information about the chess game, determines whos turn to move and keeps a move log
"""

class GameState():
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.checkMate = False
        self.staleMate = False

        self.moveFunctions = {
            "P" : self.getPawnMoves,
            "R" : self.getRookMoves,
            "N" : self.getKnightMoves,
            "B" : self.getBishopMoves,
            "Q" : self.getQueenMoves,
            "K" : self.getKingMoves
        }
    
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            
            #if in check, remove 
            if self.inCheck():
                #print(moves[i].pieceMoved, " valid : ", moves[i].startRow, " ", moves[i].startCol, " ", moves[i].endRow, " ", moves[i].endCol)
                moves.remove(moves[i])
            

            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if (len(moves) == 0):
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        
        return moves
        

    
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
            

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        
        return False

    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]

                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves

    def getPawnMoves(self, r, c, moves):
        #white pawn moves
        if self.whiteToMove:
            #one move up
            if self.board[r-1][c] == "--":
                moves.append(Move((r,c), (r-1,c), self.board))
                #two moves up
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c), (r-2,c), self.board))

            #left capture
            if c-1 >= 0 and self.board[r-1][c-1][0] == "b":
                moves.append(Move((r,c), (r-1,c-1), self.board))
            
            #right capture
            if c+1 < len(self.board[r]) and self.board[r-1][c+1][0] == "b":
                moves.append(Move((r,c), (r-1,c+1), self.board))
        
        #black pawn moves
        if not self.whiteToMove:
            #one move up
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c), (r+1,c), self.board))
                #two moves up
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c), (r+2,c), self.board))

            #left capture
            if c-1 >= 0 and self.board[r+1][c-1][0] == "w":
                moves.append(Move((r,c), (r+1,c-1), self.board))

            #right capture
            if c+1 < len(self.board[r]) and self.board[r+1][c+1][0] == "w":
                moves.append(Move((r,c), (r+1,c+1), self.board))
            

    def getRookMoves(self, r, c, moves):
        positions = [(1,0), (-1,0), (0,1), (0,-1)]

        for pos in positions:
            rowdir = pos[0]
            coldir = pos[1]

            row = r
            col = c
            while (0 <= row + rowdir < 8) and (0 <= col + coldir < 8):
                row = row+rowdir
                col = col+coldir
                if self.board[row][col] == "--":
                    moves.append(Move((r, c), (row, col), self.board))
                elif (self.whiteToMove and self.board[row][col][0] == "b") or (not self.whiteToMove and self.board[row][col][0] == "w"):
                    moves.append(Move((r,c), (row,col), self.board))
                    break
                else:
                    break
        

    def getKnightMoves(self, r, c, moves):
        positions = [(r-2, c-1), (r-2, c+1), (r+2, c-1), (r+2, c+1), (r-1, c-2), (r-1, c+2), (r+1, c-2), (r+1, c+2)]

        for pos in positions:
            endrow = pos[0]
            endcol = pos[1]
            if 0 <= endrow < 8:
                if 0 <= endcol < 8:
                    if (self.whiteToMove and self.board[endrow][endcol][0] != "w") or (not self.whiteToMove and self.board[endrow][endcol][0] != "b"):
                        moves.append(Move((r,c), (endrow, endcol), self.board))


    def getBishopMoves(self, r, c, moves):
        positions = [(1,1), (-1, -1), (-1, 1), (1, -1)]

        for pos in positions:
            rowdir = pos[0]
            coldir = pos[1]

            row = r
            col = c
            while (0 <= row + rowdir < 8) and (0 <= col + coldir < 8):
                row = row+rowdir
                col = col+coldir
                if (self.board[row][col] == "--"):
                    moves.append(Move((r,c), (row, col), self.board))
                elif (self.whiteToMove and self.board[row][col][0] == "b") or (not self.whiteToMove and self.board[row][col][0] == "w"):
                    moves.append(Move((r,c), (row, col), self.board))
                    break
                else:
                    break
    

    def getQueenMoves(self, r, c, moves):
        positions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1, -1), (-1, 1), (1, -1)]

        for pos in positions:
            rowdir = pos[0]
            coldir = pos[1]

            row = r
            col = c
            while (0 <= row + rowdir < 8) and (0 <= col + coldir < 8):
                row = row+rowdir
                col = col+coldir
                if (self.board[row][col] == "--"):
                    moves.append(Move((r,c), (row, col), self.board))
                elif (self.whiteToMove and self.board[row][col][0] == "b") or (not self.whiteToMove and self.board[row][col][0] == "w"):
                    moves.append(Move((r,c), (row, col), self.board))
                    break
                else:
                    break


    def getKingMoves(self, r, c, moves):
        positions = [(r+1, c), (r+1, c-1), (r+1, c+1), (r, c-1), (r, c+1), (r-1, c), (r-1, c-1), (r-1, c+1)]

        for pos in positions:
            endrow = pos[0]
            endcol = pos[1]

            if (0 <= endrow < 8) and (0 <= endcol < 8):
                if (self.whiteToMove and self.board[endrow][endcol][0] != "w") or (not self.whiteToMove and self.board[endrow][endcol][0] != "b"):
                    moves.append(Move((r,c), (endrow, endcol), self.board))



class Move():
    #map that assigns array pos to a chess pos
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding equals operator
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    """
    Given a row and col, returns file and its row
    """
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]