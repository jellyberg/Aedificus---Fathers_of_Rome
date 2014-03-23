import pygame, my, copy, math, mob, ui
from pygame.locals import *


def loadImg(buildingName):
	"""Just to save copy pasting in my.BUILDINGSTATS"""
	return pygame.image.load('assets/buildings/' + buildingName + '.png').convert_alpha()


my.BUILDINGNAMES = ['hut', 'shed', 'orchard', 'fishing boat', 'town hall']
my.BUILDINGSTATS = {}
my.BUILDINGSTATS['hut']       =  {'description':'A placeholder hut',
								'buildTime': 500, 'buildMaterials': {'wood': 5},
								'img': loadImg('hut')}
my.BUILDINGSTATS['shed']      = {'description':'Increases wood max amount by 30.',
								'buildTime': 2000, 'buildMaterials': {'wood': 50},
								'img': loadImg('shed')}
my.BUILDINGSTATS['orchard']   = {'description':'Feeds nearby humans.',
								'buildTime': 100, 'buildMaterials': {'wood': 100},
								'img': loadImg('orchard')}
my.BUILDINGSTATS['fishing boat'] = {'description':'Feeds nearby humans when manned by a fisherman.',
								'buildTime': 1500, 'buildMaterials': {'wood': 100},
								'img': loadImg('fishingBoat')}
my.BUILDINGSTATS['town hall'] = {'description':'Control town legislation and all that jazz.',
								'buildTime': 10000, 'buildMaterials': {'wood': 500, 'iron': 10},
								'img': loadImg('townHall')}

my.allBuildings = pygame.sprite.Group() 
my.builtBuildings = pygame.sprite.Group() 
my.buildingBeingPlaced = pygame.sprite.GroupSingle()
my.buildingsUnderConstruction = pygame.sprite.Group()

my.foodBuildings = pygame.sprite.Group()
my.foodBuildingsWithSpace = pygame.sprite.Group()
my.storageBuildings = pygame.sprite.Group()
my.storageBuildingsWithSpace = pygame.sprite.Group()

my.townHall = pygame.sprite.GroupSingle()
my.huts = pygame.sprite.Group()
my.sheds = pygame.sprite.Group()
my.orchards = pygame.sprite.Group()
my.fishingBoats = pygame.sprite.Group()

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
	def __init__(self, name, size, buildCost, buildTime, AOEsize=None):
		"""buildCost {'material1': amount1, 'material2': amount2} ad infinity
		   buildTime is actually amount of production needed to construct"""
		pygame.sprite.Sprite.__init__(self)
		self.name, self.buildingImage = name, pygame.image.load('assets/buildings/' + name + '.png').convert_alpha()
		self.buildCost, self.totalBuildProgress = buildCost, buildTime
		self.buildProgress = 0
		self.xsize, self.ysize = size
		self.add(my.buildingBeingPlaced)
		self.scaledCross = pygame.transform.scale(cross, (self.xsize * my.CELLSIZE, self.ysize * my.CELLSIZE))
		self.constructionImg = pygame.transform.scale(unscaledConstructionImg, 
			(self.xsize * my.CELLSIZE, self.ysize * my.CELLSIZE))
		self.allCoords = []
		if AOEsize:
			self.AOE = True
			self.AOEsize = AOEsize
		else: self.AOE = False
		self.buildableTerrain = 'grass'


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
				if self.rect.collidepoint(my.input.hoveredPixel):
					self.drawAOE()
			self.blit()
			self.handleTooltip()


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
		self.initTooltip()


	def canPlace(self, topLeftCoord):
		"""Check if the building can be placed if its top left is at topLeftCoord"""
		leftx, topy = topLeftCoord
		if leftx  + self.xsize >= my.MAPXCELLS or topy + self.ysize >= my.MAPYCELLS:
			return False
		for x in range(leftx, leftx + self.xsize):
			for y in range(topy, topy + self.ysize):
				if my.map.cellType((x, y)) not in self.buildableTerrain:
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


	def initTooltip(self):
		"""Initialises a tooltip that appears when the mob is hovered"""
		tooltipPos = (self.rect.right + ui.GAP, self.rect.top)
		self.tooltip = ui.Tooltip('This ' + self.name + ' is under construction', tooltipPos)


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		self.tooltip.simulate(self.rect.collidepoint(my.input.hoveredPixel), True)




class FoodBuilding(Building):
	"""Base class for food buildings"""
	def __init__(self, name, size, buildCost, buildTime, AOEsize, feedSpeed, maxCustomers):
		Building.__init__(self, name, size, buildCost, buildTime, AOEsize)
		self.feedSpeed, self.maxCustomers = feedSpeed, maxCustomers


	def updateFood(self):
		"""Update self.currentCustomers and feed those in it. Update my.foodBuildingsWithSpace too."""
		if my.builtBuildings.has(self):
			lastCustomers = self.currentCustomers.copy()
			self.currentCustomers = pygame.sprite.Group()
			# keep feeding previous customers 
			for customer in lastCustomers.sprites():
				if customer in self.AOEmobsAffected.sprites() and customer.hunger < my.FULLMARGIN + 10\
							 and customer.intention in ['eating', 'find food']:
					self.feedCustomer(customer)
			# if there's still space, feed any new customers
			if len(self.currentCustomers) < self.maxCustomers:
				for customer in self.AOEmobsAffected.sprites():
					if customer.hunger < my.FULLMARGIN + 10 and customer.intention in ['eating', 'find food']\
							 and len(self.currentCustomers) < self.maxCustomers and customer not in self.currentCustomers:
						self.feedCustomer(customer)
			self.tooltip.text = '%s/%s customers being fed, currentCustomers: %s' \
								%(len(self.currentCustomers), self.maxCustomers, self.currentCustomers)
			if len(self.currentCustomers) >= self.maxCustomers:
				self.remove(my.foodBuildingsWithSpace)
			else:
				self.add(my.foodBuildingsWithSpace)


	def onPlaceFood(self):
		self.add(my.foodBuildings)
		self.add(my.foodBuildingsWithSpace)
		self.currentCustomers = pygame.sprite.Group()


	def feedCustomer(self, customer):
		"""Feeds the customer, adds them to self.currentCustomers"""
		customer.hunger += self.feedSpeed
		customer.thought = 'eating'
		self.currentCustomers.add(customer)


class StorageBuilding(Building):
	"""Base class for storage buildings"""
	def __init__(self, name, size, buildCost, buildTime, storageCapacity):
		Building.__init__(self, name, size, buildCost, buildTime)
		self.storageCapacity = storageCapacity
		self.stored = {}
		for resource in my.resources.keys():
			self.stored[resource] = 0
		self.totalStored = 0


	def updateStorage(self):
		self.totalStored = 0
		for resourceAmount in self.stored.values():
			self.totalStored += resourceAmount
		self.tooltip.text = '%s/%s storage crates are full. This %s contains %s.'\
							 %(self.totalStored, self.storageCapacity, self.name, self.stored)
		if self.totalStored >= self.storageCapacity and my.storageBuildingsWithSpace.has(self):
			self.remove(my.storageBuildingsWithSpace)
		elif self.totalStored < self.storageCapacity and not my.storageBuildingsWithSpace.has(self):
			my.storageBuildingsWithSpace.add(self)


	def storeResource(self, resource, quantity):
		if self.totalStored + quantity < self.storageCapacity:
			self.stored[resource] += quantity


	def removeResource(self, resource, quantity):
		if self.stored[resource] >= quantity:
			self.stored[resource] -= quantity



#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM    BUILDINGS    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM

class Hut(Building):
	"""Spawns a human when placed"""
	def __init__(self):
		stats = my.BUILDINGSTATS['hut']
		Building.__init__(self, 'hut', (2, 2), stats['buildMaterials'], stats['buildTime'])
		self.add(my.huts)


	def update(self):
		self.updateBasic()


	def onPlace(self):
		x, y = self.coords
		newHuman = mob.Human((x, y + 1))
		newHuman.destination = (x - 1, y + 2)
		self.humansName = newHuman.name
		self.tooltip.text = 'The home of ' + self.humansName



class Shed(StorageBuilding):
	"""Basic storage building"""
	def __init__(self):
		stats = my.BUILDINGSTATS['shed']
		StorageBuilding.__init__(self, 'shed', (3, 3), {'wood': 100}, 500, 150)
		self.add(my.sheds)


	def update(self):
		if my.builtBuildings.has(self):
			self.updateStorage()
		self.updateBasic()


	def onPlace(self):
		pass



class Orchard(FoodBuilding):
	"""Basic food place"""
	def __init__(self):
		stats = my.BUILDINGSTATS['orchard']
		FoodBuilding.__init__(self, 'orchard', (4, 2), stats['buildMaterials'], stats['buildTime'], (3, 2), 4, 5)


	def onPlace(self):
		self.onPlaceFood()


	def update(self):
		self.updateBasic()
		if my.builtBuildings.has(self):
			self.updateFood()



class FishingBoat(FoodBuilding):
	def __init__(self):
		stats = my.BUILDINGSTATS['fishing boat']
		FoodBuilding.__init__(self, 'fishingBoat', (2, 1), stats['buildMaterials'], stats['buildTime'], (1, 2), 10, 4)
		self.buildableTerrain = 'water'


	def onPlace(self):
		self.onPlaceFood()


	def update(self):
		self.updateBasic()
		if my.builtBuildings.has(self):
			self.updateFood()



class TownHall(Building):
	"""Control town legislation etc"""
	def __init__(self):
		stats = my.BUILDINGSTATS['town hall']
		Building.__init__(self, 'townHall', (4, 3), stats['buildMaterials'], stats['buildTime'])
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
