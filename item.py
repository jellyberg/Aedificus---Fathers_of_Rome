# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import pygame, my, ui, sound, random

my.allItems = pygame.sprite.Group()
my.itemsOnTheFloor = pygame.sprite.Group()
my.fishOnTheFloor = pygame.sprite.Group()
my.oreOnTheFloor = pygame.sprite.Group()
my.swords = pygame.sprite.Group()

my.designatedTrees = pygame.sprite.Group()
my.designatedOres = pygame.sprite.Group()


def update():
	"""Keep my.handler.update() tidy"""
	for item in my.allItems.sprites():
		item.update()

def loadImg(name):
	return pygame.image.load('assets/items/' + name  + '.png').convert_alpha()


def spendResource(resource, quantity):
	"""Spend a resource by subtracting from global resource count and subtracting from any stored buildings"""
	if len(my.storageBuildings) == 0:
		my.resources[resource] -= quantity
	for building in my.storageBuildings.sprites():
		excess = None
		if building.stored[resource]:
			excess = building.removeResource(resource, quantity)
		if not excess:
			break
		else:
			quantity -= excess


class Item(pygame.sprite.Sprite):
	"""Base class for items dropped when resources are harvested etc"""
	IMG = {}
	for item in ['wood', 'fish', 'coal', 'iron', 'gold', 'nail', 'ingot', 'standard', 'sword']:
		IMG[item] = loadImg(item)
	def __init__(self, name, quantity, coords, destinationGroup='default', imageName=None):
		"""imageName need only be specified if it's not the same as the item name"""
		pygame.sprite.Sprite.__init__(self)
		self.add(my.allItems)
		self.add(my.itemsOnTheFloor)
		self.name, self.quantity, self.coords = name, quantity, coords
		self.rect = pygame.Rect(my.map.cellsToPixels(self.coords), (my.CELLSIZE, my.CELLSIZE))

		if not imageName:
			imageName = self.name
		self.image = Item.IMG[imageName]
		self.carryImage = pygame.transform.scale(self.image, (10, 10))

		if destinationGroup == 'default':
			self.destinationGroup = my.storageBuildingsWithSpace
		else:
			self.destinationGroup = destinationGroup

		self.bob = 10 # item will float up and down on the spot
		self.bobDir = 'up'
		self.reserved = None
		self.beingCarried = False
		self.lastCoords = None
		if self.sound and my.camera.isVisible(self.rect):
			sound.play(self.sound, 0.2)
		#self.tooltip = ui.Tooltip('BLANK TOOLTIP', (self.rect.left + 3, self.rect.top))


	def update(self):
		if my.allItems.has(self):
			if self.coords != self.lastCoords:
				self.rect.topleft = my.map.cellsToPixels(self.coords)
			if not self.beingCarried:
				if my.ticks % 4 == 0:
					if self.bobDir == 'up': move = 1
					else: move = -1
					self.rect.move_ip(0, move)		
					if self.bobDir == 'up':
						self.bob += 1
					elif self.bobDir == 'down':
						self.bob -= 1
					if self.bob > 5:
						self.bobDir = 'down'
					elif self.bob < -5:
						self.bobDir = 'up'
				if not self.beingCarried and self.rect.colliderect(my.camera.viewArea):
					my.surf.blit(self.image, self.rect)
				if self.reserved and self.reserved.destination != self.coords:
					self.reserved = None
				
				#if self.reserved:
				#	self.tooltip.text = 'my coords: %s, reservee coords %s' % (self.coords, self.reserved.coords)
				#if not self.beingCarried:
				#	self.tooltip.simulate(1, True)

			if self.beingCarried:
				self.rect.topleft = (0, 0)
				self.coords = None
				self.remove(my.itemsOnTheFloor)
			else:
				self.add(my.itemsOnTheFloor)
			self.lastCoords = self.coords
		



class Wood(Item):
	def __init__(self, quantity, coords):
		self.sound = None
		Item.__init__(self, 'wood', quantity, coords)


	def update(self):
		Item.update(self)


class Fish(Item):
	def __init__(self, quantity, coords):
		self.sound = 'splash'
		Item.__init__(self, 'fish', quantity, coords, my.fishMongers)


	def update(self):
		Item.update(self)
		if my.itemsOnTheFloor.has(self):
			self.add(my.fishOnTheFloor)
		else:
			self.remove(my.fishOnTheFloor)


class Ore(Item):
	def __init__(self, quantity, coords, mineral):
		self.sound = 'clunk'
		Item.__init__(self, mineral, quantity, coords, my.blacksmithsWithSpace)
		self.mineral = mineral


	def update(self):
		Item.update(self)
		if my.itemsOnTheFloor.has(self):
			self.add(my.oreOnTheFloor)
		else:
			self.remove(my.oreOnTheFloor)


class Nail(Item):
	def __init__(self, quantity, coords):
		self.sound = 'clunk'
		Item.__init__(self, 'nail', quantity, coords)


	def update(self):
		Item.update(self)


class Ingot(Item):
	def __init__(self, quantity, coords):
		self.sound = 'clunk'
		Item.__init__(self, 'ingot', quantity, coords)


	def update(self):
		Item.update(self)


class Standard(Item):
	def __init__(self, quantity, coords):
		self.sound = 'clunk'
		Item.__init__(self, 'standard', quantity, coords)


	def update(self):
		Item.update(self)


class Sword(Item):
	def __init__(self, quantity, coords):
		self.sound = 'clunk'
		self.damage = 10
		Item.__init__(self, 'sword', quantity, coords, None)
		self.add(my.swords)


	def update(self):
		Item.update(self)


class Order:
	"""Items are ordered from various buildings then produced there"""
	cogImg = pygame.image.load('assets/ui/cog.png').convert_alpha()
	def __init__(self, itemName, prerequisites, building, constructionTicks, itemQuantity):
		self.image = Item.IMG[itemName]
		self.name = itemName
		self.prerequisites, self.building = prerequisites, building
		self.constructionTicks, self.itemQuantity = constructionTicks, itemQuantity
		self.constructionProgress = -1 # not started

		self.inProgressImg = Order.cogImg.copy()
		self.inProgressImgRect = self.inProgressImg.get_rect()
		scaledImg = pygame.transform.scale(self.image.copy(), (15, 15))
		scaledImgRect = scaledImg.get_rect()
		scaledImgRect.center = self.inProgressImgRect.center
		self.inProgressImg.blit(scaledImg, scaledImgRect)


	def update(self, building, dt):
		self.building = building
		if self.constructionProgress < 0:
			if self.canConstruct():
				self.constructionProgress += 1 # start construction
				for resource in self.prerequisites.keys(): # spend resources
					self.building.stored[resource] -= self.prerequisites[resource]

		if self.constructionProgress >= 0:
			self.constructionProgress += 1 * dt * 35
			if self.constructionProgress >= self.constructionTicks: # construction complete
				itemSpawnPos = random.choice(self.building.allCoords)

				if self.name == 'wood':
					Wood(self.itemQuantity, itemSpawnPos)
				elif self.name == 'fish':
					Fish(self.itemQuantity, itemSpawnPos)
				elif self.name == 'coal':
					Ore(self.itemQuantity, itemSpawnPos, 'coal')
				elif self.name == 'iron':
					Ore(self.itemQuantity, itemSpawnPos, 'iron')
				elif self.name == 'nail':
					Nail(self.itemQuantity, itemSpawnPos)
				elif self.name == 'ingot':
					Ingot(self.itemQuantity, itemSpawnPos)
				elif self.name == 'standard':
					Standard(self.itemQuantity, itemSpawnPos)
				elif self.name == 'sword':
					Sword(self.itemQuantity, itemSpawnPos)
					
				self.building.orders.remove(self)
				self.constructionProgress = -1


	def canConstruct(self):
		for resource in self.prerequisites.keys():
			if self.building.stored[resource] < self.prerequisites[resource]:
				ui.StatusText('Not enough %s in the %s to make a %s' %(resource, self.building.name, self.name), self.building.coords)
				return False
		return True
