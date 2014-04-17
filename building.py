import pygame, my, copy, math, mob, ui, shadow, item, sound
from pygame.locals import *


def loadImg(buildingName):
	"""Just to save copy pasting in my.BUILDINGSTATS"""
	return pygame.image.load('assets/buildings/' + buildingName + '.png').convert_alpha()


my.BUILDINGNAMES = ['hut', 'shed', 'orchard', 'fishing boat', 'fish mongers','pool' , 'town hall']
my.BUILDINGSTATS = {}
my.BUILDINGSTATS['hut']       =  {'description':'Spawns a human when placed.',
								'buildTime': 5000, 'buildMaterials': {'wood': 25},
								'img': loadImg('hut')}
my.BUILDINGSTATS['shed']      = {'description':'Store all sorts of goods here.',
								'buildTime': 10000, 'buildMaterials': {'wood': 75},
								'img': loadImg('shed')}
my.BUILDINGSTATS['orchard']   = {'description':'Feeds up to 5 nearby humans.',
								'buildTime': 5000, 'buildMaterials': {'wood': 150},
								'img': loadImg('orchard')}
my.BUILDINGSTATS['fishing boat'] = {'description':'Fishermen fish fish here. Kinda fishy.',
								'buildTime': 6000, 'buildMaterials': {'wood': 100},
								'img': loadImg('fishingBoat')}
my.BUILDINGSTATS['fish mongers'] = {'description':'Feeds nearby people when fish is brought here.',
								'buildTime': 8000, 'buildMaterials': {'wood': 150},
								'img': loadImg('fishMongers')}
my.BUILDINGSTATS['pool']       =  {'description':'UNDER DEVELOPMENT.',
								'buildTime': 5000, 'buildMaterials': {'wood': 100, 'iron': 10},
								'img': loadImg('pool')}
my.BUILDINGSTATS['town hall'] = {'description':'Control town legislation and all that jazz.',
								'buildTime': 15000, 'buildMaterials': {'wood': 500, 'iron': 10},
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
my.fishMongers = pygame.sprite.Group()
my.pools = pygame.sprite.Group()

cross = pygame.image.load('assets/ui/cross.png').convert_alpha() # indicates invalid construction site
unscaledConstructionImg = pygame.image.load('assets/buildings/underConstruction.png').convert_alpha()


def updateBuildings():
	"""To keep logic.update() nice and tidy"""
	if my.input.mousePressed == 3: # right click
		my.buildingBeingPlaced.empty()
		my.mode = 'look'
	for building in my.builtBuildings.sprites():
		building.handleShadow()
	my.buildingBeingPlaced.update()
	my.allBuildings.update()



class Building(pygame.sprite.Sprite):
	"""Base class for buildings with basic functions"""
	def __init__(self, name, size, buildCost, buildTime, AOEsize=None):
		"""
		buildCost {'material1': amount1, 'material2': amount2} ad infinity
		buildTime is actually amount of production needed to construct
		AOEsize is number of cells from centre the area of effect should cover
		"""
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
			if my.builtBuildings.has(self):
				if self.AOE:
					self.updateAOE()
					if self.rect.collidepoint(my.input.hoveredPixel):
						self.drawAOE()
			self.handleTooltip()
			self.blit()


	def placeMode(self):
		"""Show ghost building on hover"""
		my.mode = 'build'
		if my.input.hoveredCell:
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
			item.spendResource(key, self.buildCost[key])

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

		if my.camera.isVisible(self.rect):
			if self.buildableTerrain == 'water':
				sound.play('splash')
			else:
				sound.play('thud')


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
				self.shadow = shadow.Shadow(self, self.buildingImage)
				#my.hud.genSurf()
				return
			else:
				progress = self.buildProgress / self.totalBuildProgress
				height = int(progress * self.buildingImage.get_height())
				progressRect = pygame.Rect((0, self.buildingImage.get_height() - height),
					(self.buildingImage.get_width(), height))
				self.image = self.constructionImg
				self.image.blit(self.buildingImage, progressRect.topleft, progressRect)


	def blit(self):
		if my.camera.isVisible(self.rect):
			my.surf.blit(self.image, self.rect)


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
		self.AOEhumansAffected = pygame.sprite.Group()
		self.AOEbuildingsAffected = pygame.sprite.Group()
		self.AOEsurf = pygame.Surface((xdist * my.CELLSIZE * 2, ydist * my.CELLSIZE * 2))
		self.AOEsurf.fill(my.YELLOW)
		self.AOEsurf.set_alpha(100)


	def updateAOE(self):
		"""Updates the groups of mobs and buildings in the AOE"""
		for mob in my.allMobs.sprites():
			if mob.coords in self.AOEcoords:
				self.AOEmobsAffected.add(mob)
				if my.allHumans.has(mob):
					self.AOEhumansAffected.add(mob)
			elif self.AOEmobsAffected.has(mob):
				self.AOEmobsAffected.remove(mob)
				if my.allHumans.has(mob):
					self.AOEhumansAffected.remove(mob)
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
		my.surf.blit(self.AOEsurf, my.map.cellsToPixels(self.AOEcoords[0]))


	def initTooltip(self):
		"""Initialises a tooltip that appears when the mob is hovered"""
		tooltipPos = (self.rect.right + ui.GAP, self.rect.top)
		self.tooltip = ui.Tooltip('This ' + self.name + ' is under construction', tooltipPos)
		self.tooltip.topleft = tooltipPos


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		self.tooltip.simulate(self.rect.collidepoint(my.input.hoveredPixel), True)


	def handleShadow(self):
		"""Draw the shadow to my.surf"""
		self.shadow.draw(my.surf, my.sunPos)



class FoodBuilding(Building):
	"""Base class for food buildings"""
	def __init__(self, name, size, buildCost, buildTime, AOEsize, feedSpeed, maxCustomers):
		Building.__init__(self, name, size, buildCost, buildTime, AOEsize)
		self.feedSpeed, self.maxCustomers = feedSpeed, maxCustomers


	def updateFood(self):
		"""Update self.currentCustomers and feed those in it. Update my.foodBuildingsWithSpace too."""
		if my.builtBuildings.has(self):
			self.currentCustomers = pygame.sprite.Group()
			# keep feeding previous customers 
			for customer in self.lastCustomers.sprites():
				if customer in self.AOEhumansAffected.sprites() and customer.hunger < my.FULLMARGIN\
							 and customer.intention  == 'find food':
					self.feedCustomer(customer)
			# if there's still space, feed any new customers
			for customer in self.AOEhumansAffected.sprites():
				if customer.hunger < my.FULLMARGIN and customer.intention == 'find food'\
						 and len(self.currentCustomers) < self.maxCustomers and customer not in self.currentCustomers:
					self.feedCustomer(customer)
			self.tooltip.text = '%s/%s customers being fed at this %s' \
								%(len(self.currentCustomers), self.maxCustomers, self.name)
			if len(self.currentCustomers) >= self.maxCustomers:
				self.remove(my.foodBuildingsWithSpace)
			else:
				self.add(my.foodBuildingsWithSpace)
			for customer in self.AOEhumansAffected: # reset none eating customers thoughts
				if customer.thought == 'eating' and customer not in self.currentCustomers:
					customer.thought = None
			self.lastCustomers = self.currentCustomers.copy()


	def onPlaceFood(self):
		self.add(my.foodBuildings)
		self.add(my.foodBuildingsWithSpace)
		self.currentCustomers = pygame.sprite.Group()
		self.lastCustomers = self.currentCustomers.copy()


	def feedCustomer(self, customer):
		"""Feeds the customer, adds them to self.currentCustomers"""
		customer.hunger += self.feedSpeed
		customer.thought = 'eating'
		customer.thoughtIsUrgent = False
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


	def onPlaceStorage(self):
		self.add(my.storageBuildings)


	def updateStorage(self):
		"""Updates the sprite's tooltip and the groups it is in"""
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
		"""Store a resource in this building, also adds to global quantity of that resource"""
		if self.totalStored + quantity < self.storageCapacity:
			self.stored[resource] += quantity
			my.resources[resource] += quantity


	def removeResource(self, resource, quantity):
		"""
		Extract a resource from this building, also subtracts from global quantity of that resource.
		If trying to remove more of the resource than is available, remove as much as possible then
		return what it couldn't remove.
		"""
		self.stored[resource] -= quantity
		my.resources[resource] -= quantity
		if self.stored[resource] < 0:
			excess = -self.stored[resource]
			self.stored[resource] = 0
			my.resources[resource] += excess
			return excess



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
		StorageBuilding.__init__(self, 'shed', (3, 3), {'wood': 100}, 500, 10000)
		self.add(my.sheds)


	def update(self):
		if my.builtBuildings.has(self):
			self.updateStorage()
		self.updateBasic()


	def onPlace(self):
		self.onPlaceStorage()



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



class FishingBoat(Building):
	def __init__(self):
		stats = my.BUILDINGSTATS['fishing boat']
		Building.__init__(self, 'fishingBoat', (2, 1), stats['buildMaterials'], stats['buildTime'])
		self.buildableTerrain = 'water'


	def onPlace(self):
		self.seats = {} # to allow reservations and destinations for fishermen
		x, y = self.coords
		for offsetx in range(2):
			self.seats[(x + offsetx, y)] = None
		self.add(my.fishingBoats)


	def update(self):
		self.updateBasic()
		if my.builtBuildings.has(self):
			self.tooltip.text = 'Fishing boat'



class FishMongers(FoodBuilding):
	"""Fish() are taken here, then can be eaten"""
	def __init__(self):
		stats = my.BUILDINGSTATS['fish mongers']
		FoodBuilding.__init__(self, 'fishMongers', (2, 2), stats['buildMaterials'], stats['buildTime'], (3, 2), 9, 9)


	def onPlace(self):
		self.onPlaceFood()
		self.remove(my.foodBuildingsWithSpace)
		self.add(my.fishMongers)
		self.currentCustomers = pygame.sprite.Group()
		self.totalStored = 0
		self.storageCapacity = 500


	def update(self):
		"""If has fish, act like a food building. Else, do nowt."""
		self.updateBasic()
		if my.builtBuildings.has(self):
			if self.totalStored > 0:
				self.updateFood()
				self.totalStored -= len(self.currentCustomers) * my.FISHCONSUMEDPERTICK
				self.tooltip.text = '%s/%s customers being fed at this %s. It contains %s/%s fish.' \
								%(len(self.currentCustomers), self.maxCustomers, self.name, int(self.totalStored), self.storageCapacity)
			else:
				self.remove(my.foodBuildingsWithSpace)
				self.tooltip.text = 'This fishmongers has no fish!'
				self.currentCustomers = None
				for customer in self.AOEhumansAffected: # reset none eating customers thoughts
					if customer.thought == 'eating':
						customer.thought = None


	def storeResource(self, resource, quantity):
		"""Add Fish().quantity to self.fish."""
		assert resource == 'fish', "Serf is storing item other than fish in a fishmonger. Stupid serf."
		self.totalStored += quantity



class Pool(Building):
	"""Splish splash"""
	def __init__(self):
		stats = my.BUILDINGSTATS['pool']
		Building.__init__(self, 'pool', (3, 2), stats['buildMaterials'], stats['buildTime'])
		self.add(my.pools)


	def update(self):
		self.updateBasic()


	def onPlace(self):
		pass



class TownHall(Building):
	"""Control town legislation etc"""
	def __init__(self):
		stats = my.BUILDINGSTATS['town hall']
		Building.__init__(self, 'townHall', (4, 3), stats['buildMaterials'], stats['buildTime'])
		self.add(my.townHall)
		self.menu = False


	def update(self):
		self.updateBasic()
		if my.input.mousePressed == 1 and my.input.hoveredCell and my.input.hoveredCellType == 'townHall':# or self.menu:
			self.showMenu()


	def showMenu(self):
		self.menu = True
		my.camera.focus = self.coords


	def onPlace(self):
		pass
