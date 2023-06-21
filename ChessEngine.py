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
        self.enpassantPossible = ()
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

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
        
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castling
        if move.isCastleMove:
            #kingside
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"

            #queenside
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))


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
            
            #enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
                
            
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()


            #undo castling rights
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            #undo castling moves
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
                    
    def updateCastleRights(self, move):
        #check if king has moved
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False

        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False

        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

        #check if rook has been captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
            
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False
                
                
    def getValidMoves(self):
        #store enpassant and castling markers to reset to original in the end
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs,
                                        self.currentCastlingRights.bqs)

        moves = self.getAllPossibleMoves()

        #castling
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)

        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        
        #remove moves that result in check
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            
            #if in check, remove 
            if self.inCheck():
                moves.remove(moves[i])
            

            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        #if no more moves available, and in check, its checkmate
        if (len(moves) == 0):
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves
        

    """
    Returns if a king is in check
    """
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
            
    """
    Returns if a given square is under attack
    """
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
            
            elif c-1 >= 0 and (r-1, c-1) == self.enpassantPossible:
                moves.append(Move((r,c), (r-1,c-1), self.board, isEnpassantMove = True))
            
            #right capture
            if c+1 < len(self.board[r]) and self.board[r-1][c+1][0] == "b":
                moves.append(Move((r,c), (r-1,c+1), self.board))

            elif c+1 < len(self.board[r]) and (r-1, c+1) == self.enpassantPossible:
                moves.append(Move((r,c), (r-1,c+1), self.board, isEnpassantMove = True))
        
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

            elif c-1 >= 0 and (r+1, c-1) == self.enpassantPossible:
                moves.append(Move((r,c), (r+1,c-1), self.board, isEnpassantMove = True))

            #right capture
            if c+1 < len(self.board[r]) and self.board[r+1][c+1][0] == "w":
                moves.append(Move((r,c), (r+1,c+1), self.board))
            
            elif c+1 < len(self.board[r]) and (r+1, c+1) == self.enpassantPossible:
                moves.append(Move((r,c), (r+1,c+1), self.board, isEnpassantMove = True))
            

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
        allyColor = "w" if self.whiteToMove else "b"

        for pos in positions:
            endrow = pos[0]
            endcol = pos[1]

            if (0 <= endrow < 8) and (0 <= endcol < 8):
                if (self.whiteToMove and self.board[endrow][endcol][0] != "w") or (not self.whiteToMove and self.board[endrow][endcol][0] != "b"):
                    moves.append(Move((r,c), (endrow, endcol), self.board))



    def getCastleMoves(self, r, c, moves):
        #if square under attack, can't castle
        if self.squareUnderAttack(r, c):
            return
        
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)
        
    
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, isCastleMove = True))


    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r,c-2), self.board, isCastleMove = True))


class CastleRights():
    def __init__ (self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    #map that assigns array pos to a chess pos
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)

        #enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        #castling
        self.isCastleMove = isCastleMove

        #unique id
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding equals operator for checking if a move is the same
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