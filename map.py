import my, pygame, random, math, item
from pygame.locals import *
from random import randint

my.allTrees = pygame.sprite.Group()
DIR = {'downright': (1, 1), 'downleft': (1, -1), 'upright': (-1, 1), 'upleft': (-1, -1)} # directions


def loadTerrainImgs(terrainNames):
	"""Load terrain .png's from assets/buildings/ when given a ist of names"""
	imgs = {}
	for name in terrainNames:
		imgs[name] = (pygame.image.load('assets/buildings/' + name + '.png').convert_alpha())
	return imgs


class Map:
#   WORLD GEN
	TERRAIN = ['tree', 'water', 'grass']
	IMGS = loadTerrainImgs(TERRAIN)
	def __init__(self):
		self.genBlankStructure()


	def completeGen(self):
		"""To be called after __init__() so my.map.map is accessible"""
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
				if self.map[x][y] in ['water', 'grass']:
					tile = self.map[x][y]
				else: tile = 'grass'
				self.surf.blit(Map.IMGS[tile], (x * my.CELLSIZE, y * my.CELLSIZE))


	def update(self):
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


	def getTreeObj(self, coords):
		"""Given a pair of coords, return the tree object at those coords"""
		x, y = coords
		if my.map.map[x][y] != 'tree':
			return None
		for tree in my.allTrees:
			if tree.coords == coords:
				return tree


class Camera:
	"""Allows for a scrolling game view, and camera shake."""
	def __init__(self):
		self.viewArea = pygame.Rect((0, 0), (my.WINDOWWIDTH, my.WINDOWHEIGHT))
		self.width = my.WINDOWWIDTH
		self.shake = 0
		self.focus = (0, 0)
		self.xVel, self.yVel = 0, 0


	def update(self):
		"""Updates camera pos and shake, and blits the to my.screen"""
		x, y = self.focus
		# ACELLERATE X
		if K_RIGHT in my.input.pressedKeys or K_d in my.input.pressedKeys:
			if self.xVel < 0: self.xVel = 0
			self.xVel += my.SCROLLACCEL
			if self.xVel > my.MAXSCROLLSPEED: xVel = my.MAXSCROLLSPEED
		elif K_LEFT in my.input.pressedKeys or K_a in my.input.pressedKeys:
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
		if K_DOWN in my.input.pressedKeys or K_s in my.input.pressedKeys:
			if self.yVel < 0: self.yVel = 0
			self.yVel += my.SCROLLACCEL
			if self.yVel > my.MAXSCROLLSPEED: yVel = my.MAXSCROLLSPEED
		elif K_UP in my.input.pressedKeys or K_w in my.input.pressedKeys:
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
		elif self.viewArea.bottom > my.map.surf.get_height():
			self.viewArea.bottom = my.map.surf.get_height()
			self.yVel = -my.MAPEDGEBOUNCE
		if self.viewArea.left < 0:
			self.viewArea.left = 0
			self.xVel = my.MAPEDGEBOUNCE
		elif self.viewArea.right > my.map.surf.get_width():
			self.viewArea.right = my.map.surf.get_width()
			self.xVel = -my.MAPEDGEBOUNCE
		my.screen.blit(my.surf, (0,0), self.viewArea)


	def shake(self, intensity):
		pass


class Tree(pygame.sprite.Sprite):
	"""A simple tree class that allows for saplings and woodcutting"""
	stumpImg = pygame.image.load('assets/buildings/treestump.png')
	def __init__(self, coords, isSapling=False):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.allTrees)
		self.coords, self.isSapling = coords, isSapling
		x, y = coords
		my.map.map[x][y] = 'tree'
		self.health = my.TREEMAXHEALTH
		self.isDead, self.justDied = False, True
		self.pos = my.map.cellsToPixels(self.coords)
		self.reserved = False


	def update(self):
		x, y = self.coords
		if not self.isDead:
			my.surf.blit(Map.IMGS['tree'], self.pos)
		elif my.map.map[x][y] == 'grass':
			my.surf.blit(Tree.stumpImg, my.map.cellsToPixels(self.coords))
		else:
			self.kill()


	def chop(self):
		self.health -= my.TREECHOPSPEED
		if self.health < 1 and self.justDied:
			item.Wood(my.WOODPERTREE + random.randint(0, 50), self.coords)
			x, y = self.coords
			my.map.map[x][y] = 'grass'
			self.isDead = True
			self.remove(my.designatedTrees)
			my.resources['wood'] += my.WOODPERTREE + random.randint(0, 50) 
			self.justDied = False


class River:
	changeDirectionFreq = 40 # %
	changeWidthFreq = 20 # %
	branchFreq = 20
	endRiverFreq = 2 # %
	"""Randomly generates a river and modifies the my.map.map data"""
	def __init__(self):
		self.modifyMap()


	def modifyMap(self):
		"""Modifies the my.map.map"""
		self.width = randint(2, 4)
		self.startPoint = (randint(0, my.MAPXCELLS), randint(0, my.MAPYCELLS))
		self.startDir = random.choice(list(DIR.keys()))
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
			return
		elif randomNum < River.changeDirectionFreq:
			nextDir = random.choice(possibleChanges)
		else:
			nextDir = currentDir
		if randomNum2 < River.changeWidthFreq and self.width > 2:
			self.width += randint(-1, 1)
		currentx, currenty = currentCell
		changex, changey = DIR[nextDir]
		nextx, nexty = (currentx + changex, currenty + changey)
		if nextx < 0 or nextx > my.MAPXCELLS - self.width or nexty < 0 or nexty > my.MAPYCELLS  - self.width:
			return
		for x in range(self.width):
			for y in range(self.width):
				my.map.map[nextx + x][nexty + y] = 'water'
		self.changeNextCell((nextx, nexty), nextDir)
