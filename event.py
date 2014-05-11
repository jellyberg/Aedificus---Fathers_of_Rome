import my, ui, building, pygame, random

from random import randint

my.currentEvents = []
my.allFloodTiles = pygame.sprite.Group()

class EventHandler:
	def __init__(self):
		self.lastFloodTime = 0


	def update(self):
		if pygame.locals.K_f in my.input.pressedKeys or randint(0, Flood.frequency) == 0 and my.ticks - self.lastFloodTime > Flood.minInterval:
			Flood()
		my.allFloodTiles.update()


class Flood:
	"""
	A flood that spawns on a river, destroying buildings and hurting mobs that it touches.
	Will be caused by Neptune's wrath when gods are implemented
	"""
	lifespan = 500 # higher is greater chance of lasting a long time
	frequency = 5000
	minInterval = 1000
	def __init__(self):
		my.currentEvents.append(self)

		self.originRiver = random.choice(my.rivers)
		self.originCoords = random.choice(self.originRiver.allCoords)
		self.xMagnitude = randint(4, 20) # distance from self.originCoords that is flooded
		self.yMagnitude = randint(4, 20)

		self.floodTiles = []
		originx, originy = self.originCoords
		for x in range(-self.xMagnitude, self.xMagnitude):
			for y in range(-self.yMagnitude, self.yMagnitude):
				if randint(0, 3) < 3:
					FloodTile((originx + x, originy + y))

		ui.StatusText('A flood has struck!', (self.originCoords), True)


class FloodTile(pygame.sprite.Sprite):
	image = pygame.image.load('assets/terrain/water.png').convert()
	def __init__(self, coords):
		pygame.sprite.Sprite.__init__(self)
		x, y = coords
		if  0 > x or x > my.MAPXCELLS - 1 or 0 > y or y > my.MAPYCELLS - 1:
			return

		self.add(my.allFloodTiles)
		self.coords = coords
		self.alpha = 'static'
		self.surf = FloodTile.image.copy()
		self.rect = pygame.Rect(my.map.cellsToPixels(self.coords), (my.CELLSIZE, my.CELLSIZE))

		if my.map.map[x][y] == 'tree':
			tree = my.map.getObj(coords, 'tree')
			tree.health = 1
			tree.chop()
		elif my.map.map[x][y] not in ['grass', 'rock', 'water', 'iron', 'coal', 'gold']:
			site = building.findBuildingAtCoord(coords)
			if not site: print(my.map.map[x][y])
			site.demolish()


	def update(self):
		if self.alpha == 'static' and randint(0, Flood.lifespan) == 0:
			self.alpha = 255
		if self.alpha != 'static':
			self.alpha -= 5
			if self.alpha < 1: self.kill()
		if my.camera.isVisible(self.rect):
			if self.alpha != 'static':
				self.surf.set_alpha(self.alpha)
			my.surf.blit(self.surf, self.rect)
