import pygame, my, ui, sound

my.allItems = pygame.sprite.Group()
my.itemsOnTheFloor = pygame.sprite.Group()
my.fishOnTheFloor = pygame.sprite.Group()
my.oreOnTheFloor = pygame.sprite.Group()

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
	for item in ['wood', 'fish', 'coal', 'iron']:
		IMG[item] = loadImg(item)
	def __init__(self, name, quantity, coords, imageName=None):
		# imageName need only be specified if it's not the same as the item name
		pygame.sprite.Sprite.__init__(self)
		self.add(my.allItems)
		self.add(my.itemsOnTheFloor)
		self.name, self.quantity, self.coords = name, quantity, coords
		self.rect = pygame.Rect(my.map.cellsToPixels(self.coords), (my.CELLSIZE, my.CELLSIZE))
		if not imageName:
			imageName = self.name
		self.image = Item.IMG[imageName]
		self.carryImage = pygame.transform.scale(self.image, (10, 10))
		self.bob = 10 # item will float up and down on the spot
		self.bobDir = 'up'
		self.reserved = None
		self.beingCarried = False
		self.lastCoords = None
		if self.sound and my.camera.isVisible(self.rect):
			sound.play(self.sound, 0.2)
		#self.initTooltip()


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
			if self.beingCarried:
				self.rect.topleft = (0, 0)
				self.coords = None
				self.remove(my.itemsOnTheFloor)
			else:
				self.add(my.itemsOnTheFloor)
			self.lastCoords = self.coords

			#self.tooltip.text = 'reserved: %s' %(self.reserved)
			#if not self.beingCarried:
			#	self.tooltip.simulate(1, True)


	def initTooltip(self):
		"""For bugfixing"""
		self.tooltip = ui.Tooltip('BLANK', (self.rect.left + 3, self.rect.top))




class Wood(Item):
	def __init__(self, quantity, coords):
		self.sound = None
		Item.__init__(self, 'wood', quantity, coords)


	def update(self):
		Item.update(self)



class Fish(Item):
	def __init__(self, quantity, coords):
		self.sound = 'splash'
		Item.__init__(self, 'fish', quantity, coords)


	def update(self):
		Item.update(self)
		if my.itemsOnTheFloor.has(self):
			self.add(my.fishOnTheFloor)
		else:
			self.remove(my.fishOnTheFloor)



class Ore(Item):
	def __init__(self, quantity, coords, mineral):
		self.sound = 'pop'
		Item.__init__(self, mineral, quantity, coords)
		self.mineral = mineral


	def update(self):
		Item.update(self)
		if my.itemsOnTheFloor.has(self):
			self.add(my.oreOnTheFloor)
		else:
			self.remove(my.oreOnTheFloor)
