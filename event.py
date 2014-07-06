# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import time, random, pygame, my, ui, building, map, sound

from random import randint

my.currentEvents = []
my.allFloodTiles = pygame.sprite.Group()
my.allowFloods = True

class EventHandler:
	def __init__(self):
		self.lastFloodTime = time.time()


	def update(self, dt):
		if my.allowFloods and \
					(randint(0, int(Flood.frequency * dt)) == 0 and time.time() - self.lastFloodTime > Flood.minInterval):
			Flood()
			self.lastFloodTime = time.time()
		my.allFloodTiles.update()


class Flood:
	"""
	A flood that spawns on a river, destroying buildings and hurting mobs that it touches.
	Will be caused by Neptune's wrath when gods are implemented
	"""
	lifespan = 500 # higher is greater chance of lasting a long time
	frequency = 10000 # jigher is lower frequency
	minInterval = 60 # seconds
	def __init__(self):
		my.currentEvents.append(self)

		self.originRiver = random.choice(my.rivers)
		self.originCoords = random.choice(self.originRiver.allCoords)
		self.radius = randint(4, 20) # radius from self.originCoords that is flooded

		self.floodTiles = []
		coords = map.getCircleCoords(self.originCoords, self.radius)
		for coord in coords:
			if randint(0, 3) < 3:
				FloodTile((coord[0], coord[1]))

		ui.StatusText('A flood has struck!', (self.originCoords), True)
		sound.play('splash')


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
			tree.chop(100)
		elif my.map.map[x][y] not in ['grass', 'rock', 'water', 'iron', 'coal', 'gold']:
			ui.StatusText('Your %s was destroyed by the flood!' %(my.map.map[x][y]), self.coords)
			site = building.findBuildingAtCoord(coords)
			site.demolish()


	def update(self):
		if self.alpha == 'static' and randint(0, Flood.lifespan) == 0:
			self.alpha = 255
		if self.alpha != 'static':
			self.alpha -= 5
			if self.alpha < 1: self.kill()
		#if my.camera.isVisible(self.rect):
		if self.alpha != 'static':
			self.surf.set_alpha(self.alpha)
		my.surf.blit(self.surf, self.rect)
