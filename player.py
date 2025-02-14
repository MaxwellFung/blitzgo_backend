class Player:

	def __init__(self):
		pass
	# def placeStone(self, board: Board, position, game):
	#return board.placeStone(self, position, game)
	
	def setColor(self, isBlack):
		self.isBlack = isBlack
		self.name = "Black" if isBlack else "White"
		self.symbol = "○" if isBlack else "●"
		self.stone_code = 1 if isBlack else 2
		self.territory_code = 10 if isBlack else 20
	
	# def changeTerritory(self, delta):
	#     self.territory_count += delta
		
	# def territory(self, board: Board):
	#     return self.territory_count
	
	def getStoneCode(self):
		return self.stone_code
	
	def getTerritoryCode(self):
		return self.territory_code
	
	# def calculateTerritory(self, board: Board):
	#     stones = board.stones
	#     territory = board.territory
	#     n = len(stones)
	#     territoryCount = 0
		
	#     for y in range(n):
	#         for x in range(n):
	#             if stones[y][x] == self:
	#                 territoryCount+=1
	#             elif territory[y][x] == self:
	#                 territoryCount+=1

	#     self.territory_count = territoryCount
		
	#     return self.territory_count