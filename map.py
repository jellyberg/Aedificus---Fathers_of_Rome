import my, pygame, random, math, item
from pygame.locals import *
from random import randint

my.allTrees = pygame.sprite.Group()
my.allOres = pygame.sprite.Group()
CARDINALDIR = {'down': (0, 1), 'left': (-1, 0), 'right': (1, 0), 'up': (0, -1)} # cardinal directions
DIAGONALDIR = {'downright': (1, 1), 'downleft': (-1, 1), 'upright': (1, -1), 'upleft': (-1, -1)} # diagonal directions
ALLDIR = {'down': (0, 1), 'left': (-1, 0), 'right': (1, 0), 'up': (0, -1),
		 'downright': (1, 1), 'downleft': (-1, 1), 'upright': (1, -1), 'upleft': (-1, -1)}


def loadTerrainImgs(terrainNames):
	"""Load terrain .png's from assets/buildings/ when given a ist of names"""
	imgs = {}
	for name in terrainNames:
		imgs[name] = (pygame.image.load('assets/terrain/' + name + '.png').convert_alpha())
	return imgs


class Map:
#   WORLD GEN
	TERRAIN = ['water', 'grass', 'rock', 'iron', 'coal', 'gold']
	IMGS = loadTerrainImgs(TERRAIN)
	def __init__(self):
		self.genBlankStructure()


	def completeGen(self):
		"""To be called after __init__() so my.map.map is accessible"""
		for i in range(my.NUMMOUNTAINS):
			Mountain()
		for i in range(my.NUMRIVERS):
			River()
		for x in range(my.MAPXCELLS):
			for y in range(my.MAPYCELLS):
				if my.map.map[x][y] == 'tree':
					Tree((x, y))
		self.genSurf()


	def genBlankStructure(self):
		self.map = []
		for x in range(my.MAPXCELLS):
			row = []
			for y in range(my.MAPYCELLS):
				tile = 'grass'
				if random.randint(0, my.TREEFREQUENCY) == 0:
					tile = 'tree'
				row.append(tile)
			self.map.append(row)


	def genSurf(self):
		self.surf = pygame.Surface((my.MAPWIDTH, my.MAPHEIGHT))
		for x in range(my.MAPXCELLS):
			for y in range(my.MAPYCELLS):
				if self.map[x][y] in ['rock', 'water']:
					tile = self.map[x][y]
				elif self.map[x][y] in ['fishingBoat']:
					tile = 'water'
				else: tile = 'grass'
				self.surf.blit(Map.IMGS[tile], (x * my.CELLSIZE, y * my.CELLSIZE))


	def update(self):
		for ore in my.allOres:
			ore.update()
		for tree in my.allTrees:
			tree.update()

#   UNIT CONVERSIONS
	def screenToGamePix(self, pixels):
		"""Given a tuple of screen pixel coords, returns corresponding game surf pixel coords"""
		x, y = pixels
		rectx, recty = my.camera.viewArea.topleft
		return (x + rectx, y + recty)


	def pixelsToCell(self, pixels):
		"""Given a tuple of game surf coords, returns the occupied cell's (x, y)"""
		x, y = pixels
		return int(math.floor(x / my.CELLSIZE)), int(math.floor(y / my.CELLSIZE))


	def cellsToPixels(self, coords):
		"""Given a tuple of my.map.map coords, returns the pixel coords of the cell's topleft"""
		x, y = coords
		return (x * my.CELLSIZE, y * my.CELLSIZE)


	def screenToCellCoords(self, pixels):
		"""Given a tuple of screen surf coords, returns the occupied cell's (x, y)"""
		gamex, gamey = self.screenToGamePix(pixels)
		return self.pixelsToCell((gamex, gamey))


	def screenToCellType(self, pixels):
		"""Given a tuple of screen surf coords, returns the occupied cell's type"""
		coords = self.screenToCellCoords(pixels)
		return self.cellType(coords)


	def cellType(self, coords):
		"""Given a tuple of map coords, returns the cell's type"""
		x, y = coords
		return self.map[x][y]


	def inBounds(self, coords):
		"""Check if the coords are within the map boundaries"""
		x, y =  coords
		if 0 < x < my.MAPXCELLS and 0 < y < my.MAPYCELLS:
			return True
		return False

#   PATHFINDING
	def distanceTo(self, start, end):
		"""Distance from cell A to cell B. Look at me, using PYTHAGORUS like a real man."""
		startx, starty = start
		endx, endy =  end
		return (endx - startx)*(endx-startx) + (endy - starty)*(endy - starty)



	def findNearestBuilding(self, myCoords, buildingGroup):
		"""Returns a single value of the nearest building object"""
		if len(buildingGroup) == 0: return None
		lowestDistanceBuilding = None
		lowestDistance = 1000000000 # arbritarily big number
		for sprite in buildingGroup.sprites():
			dist = self.distanceTo(myCoords, sprite.coords)
			if dist < lowestDistance:
				lowestDistance = dist
				lowestDistanceBuilding = sprite
		return lowestDistanceBuilding



	def findNearestBuildings(self, myCoords, buildingGroup):
		"""Returns a list of buildings specified, in ascending order of distance"""
		if len(buildingGroup.sprites()) == 0:
			return None
		buildings = []
		distances = []
		for building in buildingGroup.sprites():
			distance = self.distanceTo(myCoords, building.coords)
			for i in range(len(buildings)):
				if distances[i] < distance:
					if i == len(buildings):
						buildings.append(building)
						distances.append(distance)
				elif distances[i] >= distance:
					buildings.insert(i, building)
					distances.insert(i, distance)
			if len(buildings) == 0:
				buildings.append(building)
				distances.append(distance)
		return buildings



	def getObj(self, coords, objName):
		"""Given a pair of coords, return the tree or ore object at those coords"""
		x, y = coords
		if my.map.map[x][y] != objName:
			return None
		if objName == 'tree':
			group = my.allTrees
		elif objName in ['coal', 'iron']:
			group = my.allOres
		for obj in group:
			if obj.coords == coords:
				return obj



class Camera:
	"""Allows for a scrolling game view, and camera shake (not implemented yet)."""
	def __init__(self):
		self.viewArea = pygame.Rect((0, 0), (my.WINDOWWIDTH, my.WINDOWHEIGHT))
		self.width = my.WINDOWWIDTH
		self.shake = 0

		self.focus = (int(my.MAPWIDTH / 2), int(my.MAPHEIGHT / 2))
		self.lastFocus = self.focus
		self.targetFocus = None

		self.xVel, self.yVel = 0, 0
		self.boundRect = {'top':    pygame.Rect((0,0), (my.WINDOWWIDTH, my.MOUSESCROLL)), # for mouse camera movement
				  'right':  pygame.Rect((my.WINDOWWIDTH - my.MOUSESCROLL,0), (my.MOUSESCROLL, my.WINDOWHEIGHT)),
				  'bottom': pygame.Rect((0, my.WINDOWHEIGHT - my.MOUSESCROLL), (my.WINDOWWIDTH, my.MOUSESCROLL)),
				  'left':   pygame.Rect((0, 0), (my.MOUSESCROLL, my.WINDOWHEIGHT))}


	def update(self):
		"""Updates camera pos and shake, and blits the to my.screen"""
		x, y = self.focus

		if self.targetFocus is not None:
			destx, desty = my.map.cellsToPixels(self.targetFocus)
			x += (destx - x) * 0.1
			y += (desty - y) * 0.1
			self.focus = (x, y)

			if my.map.pixelsToCell(self.focus) == self.targetFocus or my.map.pixelsToCell(self.focus) == my.map.pixelsToCell(self.lastFocus):
				self.targetFocus = None

		# ACELLERATE X
		if K_RIGHT in my.input.pressedKeys or K_d in my.input.pressedKeys \
					or self.boundRect['right'].collidepoint(my.input.mousePos):
			if self.xVel < 0: self.xVel = 0
			self.xVel += my.SCROLLACCEL
			if self.xVel > my.MAXSCROLLSPEED: xVel = my.MAXSCROLLSPEED
		elif K_LEFT in my.input.pressedKeys or K_a in my.input.pressedKeys\
					or self.boundRect['left'].collidepoint(my.input.mousePos):
			if self.xVel > 0: self.xVel = 0
			self.xVel -= my.SCROLLACCEL
			if self.xVel < -my.MAXSCROLLSPEED: xVel = -my.MAXSCROLLSPEED
		# DECELLERATE X
		elif self.xVel > -my.SCROLLDRAG and self.xVel < my.SCROLLDRAG:
			self.xVel = 0
		elif self.xVel > 0:
			self.xVel -= my.SCROLLDRAG
		elif self.xVel < 0:
			self.xVel += my.SCROLLDRAG
		x += self.xVel

		# ACELLERATE Y
		if K_DOWN in my.input.pressedKeys or K_s in my.input.pressedKeys\
					or self.boundRect['bottom'].collidepoint(my.input.mousePos):
			if self.yVel < 0: self.yVel = 0
			self.yVel += my.SCROLLACCEL
			if self.yVel > my.MAXSCROLLSPEED: yVel = my.MAXSCROLLSPEED
		elif K_UP in my.input.pressedKeys or K_w in my.input.pressedKeys\
					or self.boundRect['top'].collidepoint(my.input.mousePos):
			if self.yVel > 0: self.yVel = 0
			self.yVel -= my.SCROLLACCEL
			if self.yVel < -my.MAXSCROLLSPEED: yVel = -my.MAXSCROLLSPEED
		# DECELLERATE Y
		elif self.yVel > -my.SCROLLDRAG and self.yVel < my.SCROLLDRAG:
			self.yVel = 0
		elif self.yVel > 0:
			self.yVel -= my.SCROLLDRAG
		elif self.yVel < 0:
			self.yVel += my.SCROLLDRAG
		y += self.yVel

		# UPDATE SELF.VIEWAREA AND BLIT
		self.focus = (x, y)
		self.viewArea.center = self.focus
		if self.viewArea.top < 0:
			self.viewArea.top = 0
			self.yVel = my.MAPEDGEBOUNCE
		elif self.viewArea.bottom > my.surf.get_height():
			self.viewArea.bottom = my.surf.get_height()
			self.yVel = -my.MAPEDGEBOUNCE
		if self.viewArea.left < 0:
			self.viewArea.left = 0
			self.xVel = my.MAPEDGEBOUNCE
		elif self.viewArea.right > my.surf.get_width():
			self.viewArea.right = my.surf.get_width()
			self.xVel = -my.MAPEDGEBOUNCE

		my.screen.blit(my.surf, (0,0), self.viewArea)
		self.lastFocus = self.focus


	def isVisible(self, rect):
		"""Checks if the rect collides with the visible area"""
		if rect.colliderect(self.viewArea):
			return True
		else:
			return False


	def shake(self, intensity):
		pass



class Tree(pygame.sprite.Sprite):
	"""A simple tree class that allows for saplings and woodcutting"""
	treeImgs = []
	for i in range(2):
		treeImgs.append(pygame.image.load('assets/terrain/tree%s.png' %(i)).convert_alpha())
	stumpImg = pygame.image.load('assets/terrain/treestump.png').convert_alpha()
	def __init__(self, coords, isSapling=False):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.allTrees)
		self.coords, self.isSapling = coords, isSapling
		x, y = coords
		my.map.map[x][y] = 'tree'
		self.image = random.choice(Tree.treeImgs)
		self.health = my.TREEMAXHEALTH
		self.isDead, self.justDied = False, True
		self.pos = my.map.cellsToPixels(self.coords)
		self.rect = pygame.Rect(self.pos, (my.CELLSIZE, my.CELLSIZE - 3))
		self.reserved = None


	def update(self):
		x, y = self.coords
		if self.rect.colliderect(my.camera.viewArea):
			if not self.isDead:
				my.surf.blit(self.image, self.pos)
			elif my.map.map[x][y] == 'grass':
				my.surf.blit(Tree.stumpImg, my.map.cellsToPixels(self.coords))
			else:
				self.kill()


	def chop(self, dt):
		self.health -= my.TREECHOPSPEED * dt
		if self.health < 1 and self.justDied:
			item.Wood(my.WOODPERTREE + random.randint(0, 50), self.coords)
			x, y = self.coords
			my.map.map[x][y] = 'grass'
			self.isDead = True
			self.remove(my.designatedTrees) 
			self.justDied = False
			my.treesChopped += 1



class River:
	"""Randomly generates a river and modifies the my.map.map data"""
	my.rivers = []
	changeDirectionFreq = 40 # %
	changeWidthFreq = 20 # %
	endRiverFreq = 4 # %
	def __init__(self):
		my.rivers.append(self)
		self.modifyMap()


	def modifyMap(self):
		"""Modifies the my.map.map"""
		self.allCoords = []
		self.width = randint(2, 4)
		self.startPoint = (randint(0, my.MAPXCELLS), randint(0, my.MAPYCELLS))
		self.startDir = random.choice(list(DIAGONALDIR.keys()))
		self.changeNextCell(self.startPoint, self.startDir)


	def changeNextCell(self, currentCell, currentDir):
		"""Modifies next cell of the river on the map, and can change direction/width or end the river"""
		if currentDir == 'upleft':
			possibleChanges = ['downleft', 'upright']
		elif currentDir == 'upright':
			possibleChanges = ['upleft', 'downright']
		elif currentDir == 'downright':
			possibleChanges = ['upright', 'downleft']
		elif currentDir == 'downleft':
			possibleChanges = ['downright', 'upleft']
		randomNum = randint(0, 100)
		randomNum2 = randint(0, 100)
		if randomNum < River.endRiverFreq:
			if len(self.allCoords) < 1:
				my.rivers.remove(self)
			return
		elif randomNum < River.changeDirectionFreq:
			nextDir = random.choice(possibleChanges)
		else:
			nextDir = currentDir
		if randomNum2 < River.changeWidthFreq and self.width > 2:
			self.width += randint(-1, 1)
		currentx, currenty = currentCell
		changex, changey = DIAGONALDIR[nextDir]
		nextx, nexty = (currentx + changex, currenty + changey)
		if nextx < 0 or nextx > my.MAPXCELLS - self.width or nexty < 0 or nexty > my.MAPYCELLS  - self.width:
			if len(self.allCoords) < 1:
				my.rivers.remove(self)
			return
		for x in range(self.width):
			for y in range(self.width):
				my.map.map[nextx + x][nexty + y] = 'water'
				self.allCoords.append((nextx + x, nexty + y))
		self.changeNextCell((nextx, nexty), nextDir)



class Mountain:
	"""Randomly generates a mountain and modifies my.map.map data"""
	endMountainFreq = 4 # % of the time
	thinMountainFreq = 40 # % of the time
	maxRadius = 15
	minStartRadius = 3
	def __init__(self):
		self.allCoords = []
		self.genRock()
		self.genOre()


	def genRock(self):
		"""Generate the rock tiles of the mountain"""
		self.origin = (randint(5, my.MAPXCELLS - 5), randint(5, my.MAPYCELLS - 5))
		self.radius = randint(Mountain.minStartRadius, Mountain.maxRadius)
		for direction in ALLDIR.values():
			self.changeNextCell(self.origin, direction)


	def changeNextCell(self, cell, direction):
		"""Called recursively to randomise mountain generation""" 
		x, y = cell
		self.modifyCircle(cell, self.radius)
		randomNum = randint(0, 100)
		if randomNum < Mountain.endMountainFreq:
			return
		elif randomNum < Mountain.thinMountainFreq:
			self.radius -= 1
		if self.radius < 2: return
		changex, changey = direction
		if 0 <(x + changex) < my.MAPXCELLS and 0 < (y + changey) < my.MAPYCELLS:
			self.changeNextCell((x + changex, y + changey), direction)


	def modifyCircle(self, centre, radius):
		"""Makes all my.map.map tiles in a circle rock. WARNING: """
		centrex, centrey = centre
		for x in range( -radius, radius):
			for y in range(-radius, radius):
				if x*x + y*y <= radius*radius and 0 <= (centrex + x) < my.MAPXCELLS and 0 < (centrey + y) < my.MAPYCELLS:
					my.map.map[centrex + x][centrey + y] = 'rock'
					if (centrex + x, centrey + y) not in self.allCoords:
						self.allCoords.append((centrex + x, centrey + y))


	def genOre(self):
		for coord in self.allCoords:
			num = randint(0, my.MASTEROREFREQ)
			if num < my.GOLDFREQ:
				Ore('gold', coord)
			elif num < my.IRONFREQ:
				Ore('iron', coord)
			elif num < my.COALFREQ:
				Ore('coal', coord)



class Ore(pygame.sprite.Sprite):
	def __init__(self, mineral, coords):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.allOres)
		self.mineral, self.coords = mineral, coords
		self.rect = pygame.Rect((my.map.cellsToPixels(self.coords)), (my.CELLSIZE, my.CELLSIZE))
		self.img = Map.IMGS[mineral]
		x, y = self.coords
		my.map.map[x][y] = self.mineral
		self.reserved = False
		self.durability = my.OREDURABILITY[self.mineral]


	def update(self):
		x, y = self.coords
		if my.map.map[x][y] != self.mineral or self.durability < 1:
			if self.durability < 1:
				my.map.map[x][y] = 'rock'
				my.map.genSurf()
			self.kill()
		if my.allOres.has(self):
			if self.rect.colliderect(my.camera.viewArea):
				my.surf.blit(self.img, self.rect)
