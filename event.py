import my, ui, pygame, random

from random import randint

my.currentEvents = []
my.allFloodTiles = pygame.sprite.Group()

class EventHandler:
	def __init__(self):
		self.lastFloodTime = 0


	def update(self):
		if randint(0, Flood.frequency) == 0 and my.ticks - self.lastFloodTime > Flood.minInterval:
			Flood()
		my.allFloodTiles.update()


class Flood:
	lifespan = 500 # higher is greater chance of lasting a long time
	frequency = 5000
	minInterval = 1000
	def __init__(self):
		my.currentEvents.append(self)

		self.originRiver = random.choice(my.rivers)
		self.originCoords = random.choice(self.originRiver.allCoords)
		self.xMagnitude = randint(2, 20) # distance from self.originCoords that is flooded
		self.yMagnitude = randint(2, 20)

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
		self.add(my.allFloodTiles)
		self.coords = coords
		self.alpha = 'static'
		self.surf = FloodTile.image.copy()
		self.rect = pygame.Rect(my.map.cellsToPixels(self.coords), (my.CELLSIZE, my.CELLSIZE))


	def update(self):
		if self.alpha == 'static' and randint(0, Flood.lifespan) == 0:
			self.alpha = 255
		if self.alpha != 'static':
			self.surf.set_alpha(self.alpha)
			self.alpha -= 5
			if self.alpha < 1: self.kill()
		if my.camera.isVisible(self.rect):
			my.surf.blit(self.surf, self.rect)
