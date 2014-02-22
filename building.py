import pygame, my
pygame.init()

class Building:
	"""Base class for buildings with basic functions"""
	def __init__(self, name, img, xsize, ysize):
		self.name, self.img = name, pygame.image.load('assets/buildings/' + name + '.png').convert_alpha()
		self.xsize, self.ysize = xsize, ysize

		self.addToMapFile((5, 5))


	def addToMapFile(self, topleftcell):
		"""For every (x, y) of my.map.map the building occupies, make my.map.map[x][y] = self.name"""
		leftx, topy = topleftcell
		self.rect = pygame.Rect((leftx * my.CELLSIZE, topy * my.CELLSIZE),
			(self.xsize * my.CELLSIZE, self.ysize * my.CELLSIZE))
		for x in range(self.xsize):
			for y in range(self.ysize):
				my.map.map[leftx + x][topy + y] = self.name


	def blit(self):
		my.map.surf.blit(self.img, self.rect)


class Hut(Building):
	pass