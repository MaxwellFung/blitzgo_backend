from board import Board
from player import Player
from random import random
from random import randint
import random

class MiniMax(Player):
    def __init__(self):
        self.firstMoveMade = False
        pass
       
        
    def getPosition(self, game):
        # print(self.miniMax(game, 4, True))
        # raise Exception("Stop")
        eval, bestMove = self.miniMax(game, 5, True)
        print(game.generateValidMoves(self))
        print("Best move:", bestMove, "with evaluation:", eval)
        
        
        if not self.firstMoveMade and self.isBlack:
            x = random.randint(0,game.board.size-1)
            y = random.randint(0,game.board.size-1)
            bestMove = (x,y)
            self.firstMoveMade = True
        return bestMove
        raise Exception("Stop")
        
        
    #everything relating to a particular board state. shuold be in the board object
    #and NOTHING ELSE
    
    def miniMax(self, game_state, depth, maximizingPlayer, alpha=float('-inf'), beta=float('inf')):
        if depth == 0 or game_state.checkGameOver():
            return self.static_evaluation(game_state), None
        player = self if maximizingPlayer else game_state.otherPlayer(self)

        if maximizingPlayer:
            maxEval = float('-inf')
            bestMove = None
            validMoves = game_state.generateValidMoves(player)
            for move in validMoves:
                copyGameState = game_state.simulateMove(self, move)
                eval, _ = self.miniMax(copyGameState, depth-1, False, alpha, beta)
                if eval > maxEval:
                    maxEval = eval
                    bestMove = move
                alpha = max(alpha, eval)
                if beta <= alpha:  # Beta cut-off
                    break
            return maxEval, bestMove
        else:
            minEval = float('inf')
            validMoves = game_state.generateValidMoves(player)
            for move in validMoves:
                copyGameState = game_state.simulateMove(self, move)
                eval, _ = self.miniMax(copyGameState, depth-1, True, alpha, beta)
                if eval < minEval:
                    minEval = eval
                beta = min(beta, eval)
                if beta <= alpha:  # Alpha cut-off
                    break
            return minEval, None

    
    # def miniMax(self, game_state, depth, maximizingPlayer):
    #     if depth == 0 or game_state.checkGameOver():
    #         return self.static_evaluation(game_state), None
        
    #     player = self if maximizingPlayer else game_state.otherPlayer(self)
    #     validMoves = game_state.generateValidMoves(player)

    #     if maximizingPlayer:
    #         maxEval = float('-inf')
    #         bestMove = None
    #         for move in validMoves:
    #             copyGameState = game_state.simulateMove(self, move)
    #             eval, _ = self.miniMax(copyGameState, depth-1, False)
    #             if eval > maxEval:
    #                 maxEval = eval
    #                 bestMove = move
    #         return maxEval, bestMove
    #     else:
    #         minEval = float('inf')
    #         for move in validMoves:
    #             copyGameState = game_state.simulateMove(self, move)
    #             eval, _ = self.miniMax(copyGameState, depth-1, True)
    #             if eval < minEval:
    #                 minEval = eval
    #         return minEval, None

    
    
    # def miniMax(self, game_state, depth, maximizingPlayer):
    #     # print(game_state.board, "\n", depth, maximizingPlayer)
    #     # print("depth: ", depth)
    #     if depth == 0 or game_state.checkGameOver():
    #         # if game_state.checkGameOver():
    #         #     if game_state.board.total_territory_count == 10:
    #         #         print(game_state.board)
    #         #         # print("t", game_state.board.territory_counts[self], game_state.board.total_territory_count)
    #         #         game_state.printBothTerritories()
    #         return self.static_evaluation(game_state)

        
        
    #     if maximizingPlayer:
    #         maxEval = float('-inf')
    #         validMoves = game_state.generateValidMoves()
    #         for move in validMoves:
    #             copyGameState = game_state.simulateMove(self, move)
    #             eval = self.miniMax(copyGameState, depth-1, False)
    #             maxEval = max(maxEval, eval)  
    #         return maxEval
        
    #     else:
    #         minEval = float('inf')
    #         validMoves = game_state.generateValidMoves()
    #         for move in validMoves:
    #             copyGameState = game_state.simulateMove(self, move)
    #             eval = self.miniMax(copyGameState, depth-1, True)
    #             minEval = min(minEval, eval)         
    #         return minEval

    def static_evaluation(self, game_state):
        L = game_state.board.territory_counts[self]
        if game_state.board.territory_counts[self] == 0:
            L = 0
        return L / game_state.board.total_territory_count
    
    def __deepcopy__(self, memo):
        return self


    

        
    
    