import pygame, my, copy
pygame.init()
from pygame.locals import *

my.allBuildings = pygame.sprite.Group() 
my.builtBuildings = pygame.sprite.Group() 
my.buildingBeingPlaced = pygame.sprite.GroupSingle()
my.buildingsUnderConstruction = pygame.sprite.Group()

my.townHall = pygame.sprite.GroupSingle()
my.huts = pygame.sprite.Group()
my.sheds = pygame.sprite.Group()

cross = pygame.image.load('assets/ui/cross.png').convert_alpha()
unscaledConstructionImg = pygame.image.load('assets/buildings/underConstruction.png').convert_alpha()


def updateBuildings():
	"""To keep logic.update() nice and tidy"""
	my.buildingBeingPlaced.update()
	my.allBuildings.update()
	if K_1 in my.input.pressedKeys:
		my.buildingBeingPlaced.add(Hut())
	elif K_2 in my.input.pressedKeys:
		my.buildingBeingPlaced.add(Shed())
	elif K_3 in my.input.pressedKeys:
		my.buildingBeingPlaced.add(TownHall())
	elif K_BACKSPACE in my.input.pressedKeys:
		if my.buildingBeingPlaced:
			my.buildingBeingPlaced.empty()



class Building(pygame.sprite.Sprite):
	"""Base class for buildings with basic functions"""
	def __init__(self, name, xsize, ysize, buildCost, buildTime):
		"""buildCost {'material1': amount1, 'material2': amount2} ad infinity
		   buildTime is actually amount of production needed to construct"""
		pygame.sprite.Sprite.__init__(self)
		self.name, self.buildingImage = name, pygame.image.load('assets/buildings/' + name + '.png').convert_alpha()
		self.buildCost, self.totalBuildProgress = buildCost, buildTime
		self.buildProgress = 0
		self.xsize, self.ysize = xsize, ysize
		self.add(my.buildingBeingPlaced)
		self.scaledCross = pygame.transform.scale(cross, (xsize * my.CELLSIZE, ysize * my.CELLSIZE))
		self.constructionImg = pygame.transform.scale(unscaledConstructionImg, (xsize * my.CELLSIZE, ysize * my.CELLSIZE))



	def addToMapFile(self, topleftcell):
		"""For every (x, y) of my.map.map the building occupies, make my.map.map[x][y] = self.name"""
		leftx, topy = topleftcell
		self.rect = pygame.Rect((leftx * my.CELLSIZE, topy * my.CELLSIZE),
			(self.xsize * my.CELLSIZE, self.ysize * my.CELLSIZE))
		for x in range(self.xsize):
			for y in range(self.ysize):
				my.map.map[leftx + x][topy + y] = self.name
		my.map.genSurf()


	def updateBasic(self):
		"""To be called in a specialised building's self.update() function"""
		if my.buildingBeingPlaced.has(self):
			self.placeMode()
		else:
			self.construct()
			self.blit()


	def placeMode(self):
		"""Show ghost building on hover"""
		my.mode = 'build'
		hoveredPixels = my.map.cellsToPixels(my.input.hoveredCell)
		my.surf.blit(self.buildingImage, hoveredPixels)
		if not self.canPlace(my.input.hoveredCell):
			my.surf.blit(self.scaledCross, hoveredPixels)
		if my.input.mousePressed and self.canPlace(my.input.hoveredCell):
			self.place()


	def place(self):
		"""Place the building on the map"""
		self.coords = my.input.hoveredCell
		self.addToMapFile(my.input.hoveredCell)
		self.remove(my.buildingBeingPlaced)
		self.add(my.buildingsUnderConstruction)
		self.add(my.allBuildings)
		for key in self.buildCost.keys():
			my.resources[key] -= self.buildCost[key]

		self.buildersPositions = []
		for x in range(self.xsize):
			row = []
			for y in range(self.ysize):
				row.append(None)
			self.buildersPositions.append(row)

		self.buildersPositionsCoords = []
		for x in range(self.xsize):
			row = []
			for y in range(self.ysize):
				row.append((0, 0))
			self.buildersPositions.append(row)
		print(str(self.buildersPositionsCoords))
		myx, myy = self.coords
		for x in range(self.xsize):
			for y in range(self.ysize):
				self.buildersPositionsCoords[x][y] = (myx + x, myy + y)

		self.onPlace()
		my.mode = 'look'


	def canPlace(self, topLeftCoord):
		"""Check if the building can be placed if its top left is at topLeftCoord"""
		leftx, topy = topLeftCoord
		if leftx  + self.xsize >= my.MAPXCELLS or topy + self.ysize >= my.MAPYCELLS:
			return False
		for x in range(leftx, leftx + self.xsize):
			for y in range(topy, topy + self.ysize):
				if my.map.cellType((x, y)) != 'grass':
					return False
		for key in self.buildCost.keys():
			if self.buildCost[key] > my.resources[key]:
				return False
		return True


	def construct(self):
		if my.buildingsUnderConstruction.has(self):
			if self.buildProgress > self.totalBuildProgress:
				my.buildingsUnderConstruction.remove(self)
				my.builtBuildings.add(self)
				self.image = self.buildingImage
				my.hud.genSurf()
				return
			else:
				progress = self.buildProgress / self.totalBuildProgress
				height = int(progress * self.buildingImage.get_height())
				progressRect = pygame.Rect((0, self.buildingImage.get_height() - height),
					(self.buildingImage.get_width(), height))
				self.image = self.constructionImg
				self.image.blit(self.buildingImage, progressRect.topleft, progressRect)



	def blit(self):
		if my.buildingsUnderConstruction.has(self):
			destinationSurf = my.surf
		else:
			destinationSurf = my.map.surf
		destinationSurf.blit(self.image, self.rect)




class Hut(Building):
	"""Currently just a placeholder"""
	def __init__(self):
		Building.__init__(self, 'hut', 2, 2, {'wood': 5}, 300)
		self.add(my.huts)


	def update(self):
		self.updateBasic()


	def onPlace(self):
		pass


class Shed(Building):
	"""Increase max wood storage by 30"""
	def __init__(self):
		Building.__init__(self, 'shed', 3, 3, {'wood': 50}, 2000)
		self.add(my.sheds)


	def onPlace(self):
		my.maxResources['wood'] += 30


	def update(self):
		self.updateBasic()


class TownHall(Building):
	"""Control town legislation etc"""
	def __init__(self):
		Building.__init__(self, 'townHall', 4, 3, {'wood': 50, 'iron': 10}, 10000)
		self.add(my.townHall)
		self.menu = False


	def update(self):
		self.updateBasic()
		if my.input.mousePressed and my.input.hoveredCellType == 'townHall' or self.menu:
			self.showMenu()


	def showMenu(self):
		self.menu = True
		print('menu!')


	def onPlace(self):
		pass
