import my, pygame, map, os, random, math
pygame.init()

my.allMobs = pygame.sprite.Group()
my.corpses = pygame.sprite.Group()

def updateMobs():
	for mob in my.allMobs.sprites:
		mob.update()
	for body in my.corpses:
		body.update()



class Mob(pygame.sprite.Sprite):
	"""Base class for all mobs"""
	def __init__(self, baseMoveSpeed, img, coords, size):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.allMobs)
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
		self.tick = random.randint(0, 19)


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
			# destx += int(my.CELLSIZE / 2)
			# desty += int(my.CELLSIZE / 2)
			# IS AT DESTINATION?
			if x == destx and y == desty:
				self.destination = None
				return
			elif math.fabs(x - destx) < self.moveSpeed or math.fabs(y - desty) < self.moveSpeed:
				self.moveSpeed = 1
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


	def die(self):
		"""Pretty self explanatory really"""
		self.kill()


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
		self.initEmotions()


	def updateHuman(self):
		self.baseUpdate()
		self.updateEmotions()


	def initEmotions(self):
		"""Initialise the human's wants and needs"""
		self.happiness = my.STARTINGHAPPINESS
		self.hunger = my.STARTINGHUNGER
		bubblePos = (self.rect.centerx, self.rect.top - my.BUBBLEMARGIN)
		self.thought = None
		self.thoughtIsUrgent = False
		self.bubble = ThoughtBubble(self.thought, bubblePos, self.thoughtIsUrgent)


	def updateEmotions(self):
		"""Update the human's wants and needs and kills it if need be!"""
		self.hunger -= 1
		if self.hunger < my.HUNGERWARNING and self.thought == None:
			self.thought = 'hungry'
			self.thoughtIsUrgent = False
		if self.hunger < my.HUNGERURGENT:
			self.thought = 'hungry'
			self.thoughtIsUrgent = True
		if self.hunger < 1:
			self.die()
		bubblePos = (self.rect.centerx, self.rect.top - my.BUBBLEMARGIN)
		print(str(self.thought))
		self.bubble.update(self.thought, bubblePos, self.thoughtIsUrgent)




class Builder(Human):
	"""Human that goes to constructions sites and builds them"""
	def __init__(self, coords):
		Human.__init__(self, coords, pygame.image.load('assets/mobs/builder.png'))
		self.building = None
		self.destinationSite = None


	def update(self):
		if self.building == None and my.tick[self.tick]:
			self.findDestination()
		self.updateHuman()
		self.build()
		if self.destinationSite or self.building:
			self.thought = 'working'
		elif self.thought == 'working':
			self.thought = None
			self.thoughtIsUrgent = False


	def findDestination(self):
		"""Find nearest free cell in a site and set as destination"""
		done = False
		lastDestination = self.destination
		sites = my.map.findNearestBuildings(self.coords, my.buildingsUnderConstruction)
		if sites:
			for site in sites:
				for x in range(len(site.buildersPositions)):
					for y in range(len(site.buildersPositions[0])):
						if done: break
						if site.buildersPositions[x][y] == None:
							# go to, and reserve a place at, the site
							self.destination = site.buildersPositionsCoords[x][y]
							site.buildersPositions[x][y] = self
							if self.destination != lastDestination and lastDestination:
								# remove reservation from last site
								destx, desty = self.destination
								if self.destinationSite:
									self.destinationSite.buildersPositions[self.buildPosx][self.buildPosy] = None
							self.destinationSite = site
							self.buildPosx, self.buildPosy = x, y
							done = True
						if done: break
					if done: break
				if done: break



	def build(self):
		"""If at site, construct it. If site is done, look for a new one."""
		done = False
		for site in my.buildingsUnderConstruction:
			for x in range(len(site.buildersPositions)):
				for y in range(len(site.buildersPositions[0])):
					if done: break
					if site.buildersPositionsCoords[x][y] == self.coords:
						self.building = site
						self.isBusy = True
						self.destinationSite = None
						done = True
					if done: break
				if done: break
		if self.building:
			self.building.buildProgress += my.CONSTRUCTIONSPEED
		if my.builtBuildings.has(self.building):
			self.isBusy = False
			self.building = None



class ThoughtBubble:
	"""A visual display of a mob's thoughts, a cloud with an icon in it."""
	bubble = pygame.image.load('assets/mobs/thoughtBubble/bubble.png').convert()
	urgentBubble = pygame.image.load('assets/mobs/thoughtBubble/urgentBubble.png').convert_alpha()
	icons = {}
	for icon in ['None', 'happy', 'sad', 'hungry', 'working']:
		icons[icon] = pygame.image.load('assets/mobs/thoughtBubble/' + icon + '.png')
	def __init__(self, thought, pos, isUrgent=False):
		self.alpha = 200
		self.rect = pygame.Rect((0,0), (20, 20))
		self.image = None
		self.thought = str(thought)
		self.isUrgent = isUrgent
		self.updateSurf()
		self.update(self.thought, pos, self.isUrgent) # blit


	def updateSurf(self):
		"""Called whenever a new thougth or urgency is needed"""
		print(str(self.thought))
		self.icon = ThoughtBubble.icons[str(self.thought)]
		if self.isUrgent:
			self.image = ThoughtBubble.urgentBubble.copy()
		else:
			self.image = ThoughtBubble.bubble.copy()
		self.image.blit(self.icon, (0,0))
		self.image.convert_alpha()


	def update(self, thought, pos, isUrgent=False):
		if self.alpha > 0:
			self.alpha -= 5
		if str(thought) != self.thought or isUrgent != self.isUrgent:
			print('new thought')
			self.thought = str(thought)
			self.alpha = 200
			self.updateSurf()
		self.image.set_alpha(self.alpha)
		self.rect.midbottom = pos
		my.surf.blit(self.image, self.rect)


class Corpse(pygame.sprite.Sprite()):
	image = pygame.image.load('assets/mobs/corpse.png')
	"""Eyecandy spawned when a human dies"""
	def __init__(self, pos):
		self.pos = pos
		self.add(my.corpses)

	def update(self):
		my.surf.blit(Corpse.image, pos)
