class TicTacToeBrain :

    def __init__(self, player = "x") :
        self._squares = {}
        self._winningCombos = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6])
        
        self.movesCnt = 0

    def createBoard(self) :
        for i in range(9) :
            self._squares[i] = "."
            
        self.movesCnt = 0

    def showBoard(self) :
        print(self._squares[0], self._squares[1], self._squares[2])
        print(self._squares[3], self._squares[4], self._squares[5])
        print(self._squares[6], self._squares[7], self._squares[8])
        print()

    def getAvailableMoves(self) :
        self._availableMoves = []
        for i in range(9) :
            if self._squares[i] == "." :
                self._availableMoves.append(i)
        return self._availableMoves

    def makeMove(self, position, player) :
        self._squares[position] = player
        
        if player != ".":
            self.movesCnt += 1
        else:
            self.movesCnt -= 1

    def complete(self) :
        if "." not in self._squares.values() :
            return True
        if self.getWinner() != None :
            return True
        return False

    def getWinner(self) :
        for player in ("x", "o") :
            for combos in self._winningCombos :
                if self._squares[combos[0]] == player and self._squares[combos[1]] == player and self._squares[combos[2]] == player :
                    return player
        if "." not in self._squares.values() :
            return "tie"
        return None

    def getEnemyPlayer(self, player) :
        if player == "x" :
            return "o"
        return "x"

    def minimax(self, player, alpha=-10, beta=10) :
        if self.complete() :
            if self.getWinner() == "tie" :
                return 0
            elif self.getWinner() == player:
                return 10 - self.movesCnt
            else:
                return self.movesCnt - 10
            
        alpha = max(alpha, self.movesCnt - 10)
        beta = min(beta, 10 - self.movesCnt)
        if alpha >= beta: return beta
        
        for move in self.getAvailableMoves() :
            self.makeMove(move, player)
            alpha = max(-1 * self.minimax(self.getEnemyPlayer(player), -beta, -alpha), alpha)
            self.makeMove(move, ".")

            if alpha >= beta:
                return alpha
            
        return alpha
    
    def makeMoves(self, gameStr):
        self.createBoard()
        for idx, move in enumerate(gameStr):
            player = "x" if idx%2 == 0 else "o"
            self.makeMove(int(move), player)
            
    def getScores(self, gameStr):
        self.makeMoves(gameStr)
        player = "x" if len(gameStr)%2 == 0 else "o"

        scores = []
        legalMoves = self.getAvailableMoves()
        for i in range(9):
            if i not in legalMoves:
                scores.append(-10)
            else:
                self.makeMove(i, player)
                scores.append(-1 * self.minimax(self.getEnemyPlayer(player)))
                self.makeMove(i, ".")
                
        return scores
