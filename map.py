import my, pygame, random
from pygame.locals import *
pygame.init()


def loadBuildingImgs(buildingNames):
	"""Load building .png's from assets/buildings/ when given a ist of names"""
	imgs = {}
	for name in buildingNames:
		imgs[name] = (pygame.image.load('assets/buildings/' + name + '.png').convert_alpha())
	return imgs


class Map:
	IMGS = loadBuildingImgs(['hut', 'tree', 'grass'])

	def __init__(self):
		self.genBlankStructure()
		self.surf = self.genSurf()


	def genBlankStructure(self):
		self.map = []
		for x in range(my.MAPXCELLS):
			row = []
			for y in range(my.MAPYCELLS):
				tile = ' '
				if random.randint(0, my.TREEFREQUENCY) == 0:
					tile = 'T'
				row.append(tile)
			self.map.append(row)


	def genSurf(self):
		surf = pygame.Surface((my.MAPWIDTH, my.MAPHEIGHT))
		for x in range(my.MAPXCELLS):
			for y in range(my.MAPYCELLS):
				building = 'grass'
				if self.map[x][y] == 'H':
					building = 'hut'
				if self.map[x][y] == 'T':
					building = 'tree'
				if building:
					surf.blit(Map.IMGS[building], (x * my.CELLSIZE, y * my.CELLSIZE))
		return surf



class Camera:
	"""Allows for a scrolling game view, and camera shake."""
	def __init__(self):
		self.viewArea = pygame.Rect((0, 0), (my.WINDOWWIDTH, my.WINDOWHEIGHT))
		self.width = my.WINDOWWIDTH
		self.shake = 0
		self.focus = (0, 0)
		self.xVel, self.yVel = 0, 0


	def update(self):
		"""Updates camera pos and shake, and blits the to my.screen"""
		x, y = self.focus
		# ACELLERATE X
		if K_RIGHT in my.input.pressedKeys:
			if self.xVel < 0: self.xVel = 0
			self.xVel += my.SCROLLACCEL
			if self.xVel > my.MAXSCROLLSPEED: xVel = my.MAXSCROLLSPEED
		elif K_LEFT in my.input.pressedKeys:
			if self.xVel > 0: self.xVel = 0
			self.xVel -= my.SCROLLACCEL
			if self.xVel < -my.MAXSCROLLSPEED: xVel = -my.MAXSCROLLSPEED
		# DECELLERATE X
		elif self.xVel > -my.SCROLLDRAG and self.xVel < my.SCROLLDRAG:
			self.xVel = 0
		elif self.xVel > 0:
			self.xVel -= my.SCROLLDRAG
		elif self.xVel < 0:
			self.xVel += my.SCROLLDRAG
		x += self.xVel
		# ACELLERATE Y
		if K_DOWN in my.input.pressedKeys:
			if self.yVel < 0: self.yVel = 0
			self.yVel += my.SCROLLACCEL
			if self.yVel > my.MAXSCROLLSPEED: yVel = my.MAXSCROLLSPEED
		elif K_UP in my.input.pressedKeys:
			if self.yVel > 0: self.yVel = 0
			self.yVel -= my.SCROLLACCEL
			if self.yVel < -my.MAXSCROLLSPEED: yVel = -my.MAXSCROLLSPEED
		# DECELLERATE Y
		elif self.yVel > -my.SCROLLDRAG and self.yVel < my.SCROLLDRAG:
			self.yVel = 0
		elif self.yVel > 0:
			self.yVel -= my.SCROLLDRAG
		elif self.yVel < 0:
			self.yVel += my.SCROLLDRAG
		y += self.yVel
		# UPDATE SELF.VIEWAREA AND BLIT
		self.focus = (x, y)
		self.viewArea.center = self.focus
		if self.viewArea.top < 0:
			self.viewArea.top = 0
			self.yVel = my.MAPEDGEBOUNCE
		elif self.viewArea.bottom > my.map.surf.get_height():
			self.viewArea.bottom = my.map.surf.get_height()
			self.yVel = -my.MAPEDGEBOUNCE
		if self.viewArea.left < 0:
			self.viewArea.left = 0
			self.xVel = my.MAPEDGEBOUNCE
		elif self.viewArea.right > my.map.surf.get_width():
			self.viewArea.right = my.map.surf.get_width()
			self.xVel = -my.MAPEDGEBOUNCE
		my.screen.blit(my.map.surf, (0,0), self.viewArea)


