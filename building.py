import pygame, my, copy, math
pygame.init()
from pygame.locals import *


def loadImg(buildingName):
	"""Just to save copy pasting in my.BUILDINGSTATS"""
	return pygame.image.load('assets/buildings/%s.png' %(buildingName))

my.BUILDINGNAMES = ['hut', 'shed', 'orchard', 'town hall']
my.BUILDINGSTATS = {}
my.BUILDINGSTATS['hut']       =  {'description':'A placeholder hut',
									'buildTime': 500, 'buildMaterials': {'wood': 5},
									'img': loadImg('hut')}
my.BUILDINGSTATS['shed']      = {'description':'Increases wood max amount by 30.',
									'buildTime': 2000, 'buildMaterials': {'wood': 50},
									'img': loadImg('shed')}
my.BUILDINGSTATS['orchard']   = {'description':'Feeds nearby humans.',
									'buildTime': 1500, 'buildMaterials': {'wood': 200},
									'img': loadImg('orchard')}
my.BUILDINGSTATS['town hall'] = {'description':'Control town legislation and all that jazz.',
									'buildTime': 10000, 'buildMaterials': {'wood': 500, 'iron': 10},
									'img': loadImg('townHall')}

my.allBuildings = pygame.sprite.Group() 
my.builtBuildings = pygame.sprite.Group() 
my.buildingBeingPlaced = pygame.sprite.GroupSingle()
my.buildingsUnderConstruction = pygame.sprite.Group()

my.foodBuildings = pygame.sprite.Group()

my.townHall = pygame.sprite.GroupSingle()
my.huts = pygame.sprite.Group()
my.sheds = pygame.sprite.Group()
my.orchards = pygame.sprite.Group()

cross = pygame.image.load('assets/ui/cross.png').convert_alpha() # indicates invalid construction site
unscaledConstructionImg = pygame.image.load('assets/buildings/underConstruction.png').convert_alpha()


def updateBuildings():
	"""To keep logic.update() nice and tidy"""
	if my.input.mousePressed == 3:
		my.buildingBeingPlaced.empty()
	my.buildingBeingPlaced.update()
	my.allBuildings.update()



class Building(pygame.sprite.Sprite):
	"""Base class for buildings with basic functions"""
	def __init__(self, name, xsize, ysize, buildCost, buildTime, AOEsize=None):
		"""buildCost {'material1': amount1, 'material2': amount2} ad infinity
		   buildTime is actually amount of production needed to construct"""
		pygame.sprite.Sprite.__init__(self)
		self.name, self.buildingImage = name, pygame.image.load('assets/buildings/' + name + '.png').convert_alpha()
		self.buildCost, self.totalBuildProgress = buildCost, buildTime
		self.buildProgress = 0
		self.xsize, self.ysize = xsize, ysize
		self.add(my.buildingBeingPlaced)
		self.scaledCross = pygame.transform.scale(cross, (xsize * my.CELLSIZE, ysize * my.CELLSIZE))
		self.constructionImg = pygame.transform.scale(unscaledConstructionImg, 
			(xsize * my.CELLSIZE, ysize * my.CELLSIZE))
		self.allCoords = []
		if AOEsize:
			self.AOE = True
			self.AOEsize = AOEsize
		else: self.AOE = False


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
			if self.AOE:
				self.updateAOE()
				#self.drawAOE()
			self.blit()


	def placeMode(self):
		"""Show ghost building on hover"""
		my.mode = 'build'
		hoveredPixels = my.map.cellsToPixels(my.input.hoveredCell)
		my.surf.blit(self.buildingImage, hoveredPixels)
		if not self.canPlace(my.input.hoveredCell):
			my.surf.blit(self.scaledCross, hoveredPixels)
		if my.input.mousePressed == 1 and self.canPlace(my.input.hoveredCell):
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
			self.buildersPositionsCoords.append(row)
		myx, myy = self.coords
		for x in range(self.xsize):
			for y in range(self.ysize):
				self.buildersPositionsCoords[x][y] = (myx + x, myy + y)

		leftx, topy = self.coords
		for x in range(leftx, self.xsize + leftx):
			for y in range(topy, self.ysize + leftx):
				self.allCoords.append((x, y))
		my.mode = 'look'

		if self.AOE:
			self.initAOE(self.AOEsize)


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
				self.onPlace()
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


	def initAOE(self, AOEsize):
		"""Creates an area of effect which extends xdist and ydist from building's centre"""
		leftx, topy = self.coords
		xdist, ydist = AOEsize
		centrex, centrey = leftx + int(math.ceil(self.xsize / 2)), topy + int(math.ceil(self.ysize / 2))
		self.AOEcoords = []
		for x in range(centrex - xdist, centrex + xdist):
			for y in range(centrey - ydist, centrey + ydist):
				self.AOEcoords.append((x, y))
		self.AOEmobsAffected = pygame.sprite.Group()
		self.AOEbuildingsAffected = pygame.sprite.Group()


	def updateAOE(self):
		"""Updates the groups of mobs and buildings in the AOE"""
		for mob in my.allMobs.sprites():
			if mob.coords in self.AOEcoords:
				self.AOEmobsAffected.add(mob)
			elif self.AOEmobsAffected.has(mob):
				self.AOEmobsAffected.remove(mob)
		done = False
		for building in my.builtBuildings.sprites():
			for coord in building.allCoords:
				if coord in self.AOEcoords:
					self.AOEbuildingsAffected.add(building)
					done = True
				if done: break
			if not done and self.AOEbuildingsAffected.has(building):
				self.AOEbuildingsAffected.remove(building)


	def drawAOE(self):
		for coord in self.AOEcoords:
			x, y = coord
			rect = pygame.Rect(x * my.CELLSIZE, y * my.CELLSIZE, my.CELLSIZE, my.CELLSIZE)
			pygame.draw.rect(my.surf, my.BLUETRANS, rect)




class FoodBuilding(Building):
	"""Base class for food buildings"""
	def __init__(self, name, xsize, ysize, buildCost, buildTime,xAOE, yAOE, feedSpeed):
		Building.__init__(self, name, xsize, ysize, buildCost, buildTime, (xAOE, yAOE))
		self.feedSpeed = feedSpeed # hunger sated per second


	def updateFood(self):
		if my.builtBuildings.has(self):
			for customer in self.AOEmobsAffected.sprites():
				if customer.hunger < my.MAXHUNGER:
					customer.hunger += self.feedSpeed


	def onPlaceFood(self):
		self.add(my.foodBuildings)



#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM    BUILDINGS    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM

class Hut(Building):
	"""Currently just a placeholder"""
	def __init__(self):
		stats = my.BUILDINGSTATS['hut']
		Building.__init__(self, 'hut', 2, 2, stats['buildMaterials'], stats['buildTime'])
		self.add(my.huts)


	def update(self):
		self.updateBasic()


	def onPlace(self):
		pass



class Shed(Building):
	"""Increase max wood storage by 30"""
	def __init__(self):
		stats = my.BUILDINGSTATS['shed']
		Building.__init__(self, 'shed', 3, 3, stats['buildMaterials'], stats['buildTime'])
		self.add(my.sheds)


	def onPlace(self):
		my.maxResources['wood'] += 30


	def update(self):
		self.updateBasic()



class Orchard(FoodBuilding):
	"""Basic food place"""
	def __init__(self):
		stats = my.BUILDINGSTATS['orchard']
		FoodBuilding.__init__(self, 'orchard', 4, 2, stats['buildMaterials'], stats['buildTime'], 3, 2, 2)


	def onPlace(self):
		self.onPlaceFood()


	def update(self):
		self.updateBasic()
		self.updateFood()



class TownHall(Building):
	"""Control town legislation etc"""
	def __init__(self):
		stats = my.BUILDINGSTATS['town hall']
		Building.__init__(self, 'townHall', 4, 3, stats['buildMaterials'], stats['buildTime'])
		self.add(my.townHall)
		self.menu = False


	def update(self):
		self.updateBasic()
		if my.input.mousePressed == 1 and my.input.hoveredCellType == 'townHall':# or self.menu:
			self.showMenu()


	def showMenu(self):
		self.menu = True
		my.camera.focus = self.coords


	def onPlace(self):
		pass
