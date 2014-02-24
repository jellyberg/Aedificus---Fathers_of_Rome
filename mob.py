import my, pygame, map, os, random
pygame.init()

my.allMobs = pygame.sprite.Group()

class Mob(pygame.sprite.Sprite):
	"""Base class for all mobs"""
	def __init__(self, baseMoveSpeed, img, coords, size):
		pygame.sprite.Sprite.__init__(self)
		self.animFrame = 0
		if type(img) == list:
			self.animation = img
			self.handleImage()
		else:
			self.image = img
			self.animation = None
		self.isBusy = False
		self.rect = pygame.Rect(my.map.cellsToPixels(coords), size)
		self.destination = None
		self.baseMoveSpeed = baseMoveSpeed
		self.coords =  my.map.pixelsToCell(self.rect.center)
		self.tick = random.randint(0, len(my.tick))


	def baseUpdate(self):
		self.coords =  my.map.pixelsToCell(self.rect.center)
		self.updateMove()
		self.handleImage()
		self.blit()


	def updateMove(self):
		"""Move towards self.destination coords"""
		if self.destination:
			x, y = self.rect.topleft
			destx, desty = my.map.cellsToPixels(self.destination)
			destx += int(my.CELLSIZE / 2)
			desty += int(my.CELLSIZE / 2)
			# IS AT DESTINATION?
			if x == destx and y == desty:
				self.destination = None
				return
			# IF NOT, SET UP MOVE DISTANCE
			# If moving diagonally, only move half as far in x and half as far in y
			movex, movey = 1, 1
			if x == destx: movex = 0
			if y == desty: movey = 0
			if movex and movey: distance = int(self.moveSpeed / 2)
			else: distance = self.moveSpeed
			# AND MOVE
			if x < destx:   movex =  self.moveSpeed
			elif x > destx: movex = -self.moveSpeed
			if y < desty:   movey =  self.moveSpeed
			elif y > desty: movey = -self.moveSpeed
			self.rect.move_ip(movex, movey)
		if random.randint(0, 200) == 0:
			self.moveSpeed = random.randint(self.baseMoveSpeed - 1, self.baseMoveSpeed + 1)


	def blit(self):
		"""Blit to surf, which is overlayed onto my.map.map"""
		my.surf.blit(self.image, self.rect)


	def loadAnimationFiles(self, directory, file):
		"""Load images from directory into a list of surfaces"""
		animation = []
		frames = len(os.listdir(directory))
		for num in range(0, frames):
			num = str(num)
			num = num.zfill(4)
			img = pygame.image.load(directory + '/' + file +  '.' + num + '.png').convert_alpha()
			animation.append(img)
		return animation


	def handleImage(self):
		"""If has animation, update self.image"""
		if self.animation:
			self.image = self.animation[self.animFrame]
			if my.ticks % 6 == 0:
				self.animFrame += 1
			if self.animFrame > len(self.animation) - 1:
				self.animFrame = 0



class Human(Mob):
	"""Base class for humans"""
	def __init__(self, coords, clothes):
		if not hasattr(self, 'image'):
			self.animation = self.loadAnimationFiles('assets/mobs/dude', 'dude')
			for frame in self.animation:
				frame.blit(clothes, (0, 0))
		if not hasattr(self, 'size'):
			self.size = (1, 2)
		if not hasattr(self, 'moveSpeed'):
			self.baseMoveSpeed = my.HUMANMOVESPEED
			self.moveSpeed = my.HUMANMOVESPEED
		Mob.__init__(self, self.baseMoveSpeed, self.animation, coords, self.size)



class Builder(Human):
	"""Human that goes to constructions sites and builds them"""
	def __init__(self, coords):
		Human.__init__(self, coords, pygame.image.load('assets/mobs/builder.png'))
		self.building = None


	def update(self):
		if not self.destination and not self.isBusy or my.tick[self.tick]:
			self.findDestination()
		self.baseUpdate()
		self.build()


	def findDestination(self):
		"""Find nearest site without tons of other builders and set as destination"""
		self.destination = None
		done = False
		sites = my.map.findNearestBuildings(self.coords, my.buildingsUnderConstruction)
		if sites:
			for site in sites:
				for x in range(len(site.buildersPositions)):
					for y in range(len(site.buildersPositions)):
						if site.buildersPositions[x][y] == None:
							self.destination = site.buildersPositionsCoords[x][y]
							done = True
						if done: break
					if done: break
				if done: break



	def build(self):
		"""If at site, construct it"""
		for site in my.buildingsUnderConstruction:
			if site.coords == self.coords:
				self.building = site
				self.isBusy = True
				break
			else:
				#if self.building:
				#	self.building.buildersBuilding.remove(self)
				self.building = None
				self.isBusy = False
		if self.building and my.tick:
			self.building.buildProgress += my.CONSTRUCTIONSPEED
