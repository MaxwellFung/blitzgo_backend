class Board:
	def __init__(self,size):
		self.stones = [[None for i in range(size)] for j in range(size)]
		self.territory = [[None for i in range(size)] for j in range(size)]
		self.players = []
		self.territory_counts = {}
		self.total_territory_count = 0
		self.size = size
		self.size_2 = size**2
		self.move_history = []
		self.move_set = set()
		# self.move_set.add(self.hash_board()) not needed technically.
		
		# self.zobrist_table = self.initialize_zobrist_hash(size)
		
	def initalizeTerritoryCounts(self, player):
		self.territory_counts[player] = 0

	
	def generateValidMoves(self, player):
		move_scores = {}  # Dictionary to store moves and their scores
		directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1), (1, 1), (-1, -1)]  # All 8 directions
		
		for y in range(self.size):
			for x in range(self.size):
				if self.stones[y][x] is not None:  # Only check from occupied cells
					for dx, dy in directions:
						nx, ny = x + dx, y + dy
						if 0 <= nx < self.size and 0 <= ny < self.size:  # Ensure within bounds
							if self.stones[ny][nx] is None:  # Check if the adjacent cell is empty
								if (nx, ny) not in move_scores:
									move_scores[(nx, ny)] = 1
								else:
									move_scores[(nx, ny)] += 1  # Increment score for each adjacent stone

		# Sort the moves by their scores in descending order and get the top 20
		sorted_moves = sorted(move_scores.items(), key=lambda item: item[1], reverse=True)
		top_moves = [move for move, score in sorted_moves[:20]]  # Get top 20 moves, ignoring scores

		return top_moves  # Returns a list of positions


	
	# def generateValidMoves(self, player):
	#     validMoves = []
	#     # directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 

	#     for y in range(self.size):
	#         for x in range(self.size):
	#             if self.stones[y][x] is None: 
	#                 validMoves.append((x, y))
	#                 # if self.territory[y][x] is None:
	#                 #     validMoves.append((x, y))
	#                 # elif self.territory[y][x] != player:
	#                 #     # Check if adjacent to one of the player's stones
	#                 #     for dx, dy in directions:
	#                 #         nx, ny = x + dx, y + dy
	#                 #         if 0 <= nx < self.size and 0 <= ny < self.size and self.stones[ny][nx] == player:
	#                 #             validMoves.append((x, y))
	#                 #             break
	#     return validMoves
					
	#ANY HELPERS /CHECKS
	#if within bounds and its empty
	def isValidMove(self,position):
		x,y = position
		if not self.is_within_bounds(position):
			return False
		if self.stones[y][x] is not None:
			return False
		return True
	
	def isDuplicateMove(self):
		# return False
		hashed_board = self.hash_board()
		if hashed_board in self.move_set:
		# if False:
			return True
		else:
			self.move_set.add(self.hash_board()) #add to move set.
			return False 
	
			
	def removeStone(self, position):
		x,y = position
		self.incrementTerritory(self.stones[y][x], -1)
		self.stones[y][x] = None
		
	def is_within_bounds(self, position):
		x, y = position
		return 0 <= x < self.size and 0 <= y < self.size
	
	
	#ALL PLACE STONE LOGIC
	def remove_last_move(self, position):
		x,y = position
		if self.stones[y][x] != None and self.territory[y][x] != None and self.stones[y][x] != self.territory[y][x]:
			self.incrementTerritory(self.territory[y][x], 1)
			self.removeStone(position)
			return True
		
		return False
	
	def placeStone(self, player, position):
		x, y = position   
		
		if not self.isValidMove(position):
			return 1 #for invalid move
		
		self.stones[y][x] = player 
		if self.isDuplicateMove():
			self.stones[y][x] = None #revert the move.
			return 2 #for duplicate move
				   
		captured = self.update_other_stones(player,position)
				
		self.move_history.append(position) 
		return 0 # for successful move.
		
		# self.move_set.add(self.hash_board())
		# print("Size of set: ",deep_getsizeof(self.move_set)/1000, "KB")
				
#update your territory if you made an encirclement
#remove all the stone inside your new terriroies. 
#captured, then update other player's teririroies
#remove the last move if it is in someone elses territory 

	def update_other_stones(self, player, position):
		self.incrementTerritory(player, 1)
		
		total_territory = self.update_territories(player, position) 
		captured = self.remove_stones_in_territory(player, total_territory) 
		
		if captured:
			self.bfs_update_opponent_territory(player, position) 
		if self.move_history:
			if (self.remove_last_move(self.move_history[-1])):
				captured = True
		self.removeSingleTerritory(position)
		return captured             
	
	def removeSingleTerritory(self, position):
		x,y = position
		if self.territory[y][x] != None and self.stones[y][x] != None and self.territory[y][x] != self.stones[y][x]:
			self.incrementTerritory(self.territory[y][x], -1)            
			
	def remove_stones_in_territory(self, player, total_territory):
		captured = False
		for territory in total_territory:
			x,y = territory
			if self.stones[y][x] != None and self.stones[y][x] != player:
				self.removeStone(territory)
				captured = True
		return captured
				
	
	def update_territories(self, player, position):
		x,y = position
		total_territory = set()
		
		if self.territory[y][x] == player:
			self.incrementTerritory(player, -1)
			self.territory[y][x] = None
			return total_territory
 
		totalVisited = set()
		directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  
		for dx, dy in directions:
			nx, ny = position[0] + dx, position[1] + dy
			if self.is_within_bounds((nx, ny)) and self.stones[ny][nx] != player and (nx,ny) not in totalVisited:
				enclosed_territory = self.bfs_enclosed_territory(player, (nx, ny), totalVisited)
				if enclosed_territory:
					for (tx, ty) in enclosed_territory:
						if self.territory[ty][tx] != player:
							if self.territory[ty][tx] != None:
								self.incrementTerritory(self.territory[ty][tx], -1)
							self.incrementTerritory(player, 1)
							self.territory[ty][tx] = player
						total_territory.add((tx, ty)) #might not need

		return total_territory
	
	def bfs_update_opponent_territory(self, player, start):
		queue = [start]        
		x,y = start
		
		#check at start position
		if self.is_within_bounds((x,y)) and self.territory[y][x] != player and self.territory[y][x] != None:
			self.incrementTerritory(self.territory[y][x], -1)
			self.territory[y][x] = None
			
		while queue:
			x, y = queue.pop(0)
			for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
				nx, ny = x + dx, y + dy
				
				if self.is_within_bounds((nx,ny)) and self.territory[ny][nx] != player and self.territory[ny][nx] != None:
					queue.append((nx, ny))
					self.incrementTerritory(self.territory[ny][nx], -1)
					self.territory[ny][nx] = None


	def bfs_enclosed_territory(self, player, start, totalVisited: set):
		queue = [start]
		totalVisited.add(start)
		walls_touched = set()
		visited = set(queue)

		while queue:
			x, y = queue.pop(0)
			for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  
				nx, ny = x + dx, y + dy
				
				boolTouchWall = False
				if ny < 0:
					walls_touched.add('top')
					boolTouchWall = True
				if ny >= self.size:
					walls_touched.add('bottom')
					boolTouchWall = True
				if nx < 0:
					walls_touched.add('left')
					boolTouchWall = True
				if nx >= self.size:
					walls_touched.add('right')
					boolTouchWall = True    
							   
				
				if len(walls_touched)>2:
					return None
				# else:
				#     print("walls touhced: ", len(walls_touched))
				#     print(walls_touched)
				if boolTouchWall or (nx, ny) in visited:
					continue

				if (nx, ny) not in visited and self.stones[ny][nx] != player:                    
					queue.append((nx, ny))
					totalVisited.add((nx, ny))
					visited.add((nx, ny))
		return visited  
	
	#Operates on Heidari's Fundemental Win Condition Theorem
	def stability_test(self, player, position):
		x,y = position
		player = self.territory[y][x]
		
		if player == None:
			raise Exception("WHAT THE FUCK SOMETHING BROKE HEIDARI'S THEOREM ")
		
		countCorner = 0
				
		for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:  
			nx, ny = x + dx, y + dy
			if self.is_within_bounds((nx,ny)) and self.stones[ny][nx] != None and self.stones[ny][nx] != player:
				countCorner +=1
		
		if countCorner >= 2:
			return False
		
		if countCorner == 1:
			if x == 0 or y ==0 or x == self.size-1 or y == self.size-1:
				return False

		return True
					
	def checkGameOver(self):      
		for y in range(self.size):
			for x in range(self.size):
				if self.territory[y][x] != None and not self.stability_test(self.territory[y][x], (x,y)):
		
					return False
		return True
	
	#ANYTHING TO DO WITH TERRITORY COUNTS
	def totalTerritory(self):
		return self.total_territory_count
	
	def incrementTerritory(self, player, delta):
		self.territory_counts[player] +=delta
		self.total_territory_count += delta
		
	def printBothTerritories(self):
		for player in self.territory_counts:
			print(f"{player.name}'s territory: ", self.territory_counts[player])
			
		print("Total: ", self.total_territory_count)
	
	
	
	
	
	# def initialize_zobrist_hash(self):
	#     zobrist_table = [[[randint(1, 2**64 - 1) for _ in range(3)] for _ in range(self.size)] for _ in range(self.size)]
	#     return zobrist_table
	
	# def hash_board(self):
	#     board_hash = 0
	#     for y in range(self.size):
	#         for x in range(self.size):
	#             piece = self.stones[y][x]
	#             if piece is None:
	#                 state = 0
	#             elif piece == self.players[0]:  # Assuming player1 and player2 are defined somewhere globally or passed to the function
	#                 state = 1
	#             elif piece == self.players[1]:
	#                 state = 2
	#             board_hash ^= self.zobrist_table[y][x][state]
	#     return board_hash
	
	
	
	
	#ANYTHING TO DO WITH PRINTING OR HASHING    
	def hash_board(self):
		return tuple(tuple(row) for row in self.stones)
	
	def __str__(self):
		board_str = "  " + ''.join([str(i + 1).rjust(2) for i in range(self.size)]) + "\n"  # Adding column headers
		for index, row in enumerate(self.stones):
			row_str = str(index + 1).rjust(2) + ' '  # Adding row numbers
			row_str += ' '.join(['.' if player is None else player.symbol for player in row])
			board_str += row_str + "\n"
		return board_str
		
	def flattenBoard(self):
		flattenList = [0 for x in range(self.size_2)]
		for y in range(self.size):
			for x in range(self.size):
				if self.stones[y][x] == None:
					if self.territory[y][x] ==None:
						pass
					else:
						flattenList[y*self.size + x] = self.territory[y][x].getTerritoryCode()
				else:
					flattenList[y*self.size + x] = self.stones[y][x].getStoneCode()
					
		return flattenList
	
	def TS(self):
		board_str = "  " + ''.join([str(i + 1).rjust(2) for i in range(self.size)]) + "\n"  # Adding column headers
		for index, row in enumerate(self.territory):
			row_str = str(index + 1).rjust(2) + ' '  # Adding row numbers
			row_str += ' '.join(['.' if stone is None else stone.symbol for stone in row])
			board_str += row_str + "\n"
		return board_str
	

	
