import my, pygame, map, ui, os, random, math
pygame.init()
from pygame.locals import *

my.allMobs = pygame.sprite.Group()
my.corpses = pygame.sprite.Group()

def updateMobs():
	for mob in my.allMobs.sprites():
		mob.update()
	for corpse in my.corpses.sprites():
		corpse.update()


def loadAnimationFiles(directory, file):
	"""Load images from directory into a list of surfaces"""
	animation = []
	frames = len(os.listdir(directory))
	for num in range(0, frames):
		num = str(num)
		num = num.zfill(4)
		img = pygame.image.load(directory + '/' + file +  '.' + num + '.png').convert_alpha()
		animation.append(img)
	return animation



class Mob(pygame.sprite.Sprite):
	"""Base class for all mobs"""
	def __init__(self, baseMoveSpeed, img, coords, size):
		pygame.sprite.Sprite.__init__(self)
		self.isDead = False
		self.causeOfDeath = None
		self.add(my.allMobs)
		self.animFrame = 0
		if type(img) == list:
			self.animation = img
			self.handleImage()
		else:
			self.image = img
			self.animation = None
		self.rect = pygame.Rect(my.map.cellsToPixels(coords), size)
		self.destination = None
		self.baseMoveSpeed = baseMoveSpeed
		self.coords =  my.map.pixelsToCell(self.rect.center)
		self.tick = random.randint(1, 19)
		self.initTooltip()


	def baseUpdate(self):
		if not self.isDead:
			self.coords =  my.map.pixelsToCell(self.rect.center)
			self.updateMove()
			self.handleImage()
			self.blit()
		self.handleTooltip()


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
		"""Pretty self explanatory really. Kick the bucket."""
		self.kill()
		self.isDead = True
		Corpse((self.rect.centerx, self.rect.bottom + 5), pygame.image.load('assets/mobs/dude.png'),
				 self.name, self.causeOfDeath)


	def blit(self):
		"""Blit to surf, which is overlayed onto my.map.map"""
		my.surf.blit(self.image, self.rect)


	def handleImage(self):
		"""If has animation, update self.image"""
		if self.animation:
			self.image = self.animation[self.animFrame]
			if my.ticks % 6 == 0:
				self.animFrame += 1
			if self.animFrame > len(self.animation) - 1:
				self.animFrame = 0


	def initTooltip(self):
		"""Initialises a tooltip that appears when the mob is hovered"""
		tooltipPos = (self.rect.right + ui.GAP, self.rect.centery)
		self.tooltip = ui.Tooltip('Blank tooltip', tooltipPos)


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		self.tooltip.pos = (self.rect.right + ui.GAP, self.rect.centery)
		if my.input.hoveredCell == self.coords:
			isHovered = True
		else:
			isHovered = False
		self.tooltip.simulate(isHovered, True)




class Human(Mob):
	"""Base class for humans"""
	def __init__(self, coords, clothes):
		if not hasattr(self, 'image'):
			self.animation = loadAnimationFiles('assets/mobs/dude', 'dude')
			for frame in self.animation:
				frame.blit(clothes, (0, 0))
		if not hasattr(self, 'size'):
			self.size = (1, 2)
		if not hasattr(self, 'moveSpeed'):
			self.baseMoveSpeed = my.HUMANMOVESPEED
			self.moveSpeed = my.HUMANMOVESPEED
		Mob.__init__(self, self.baseMoveSpeed, self.animation, coords, self.size)
		self.name = random.choice(my.FIRSTNAMES) + ' ' + random.choice(my.LASTNAMES)
		self.tooltip.text = self.name
		self.initEmotions()


	def updateHuman(self):
		if not self.isDead:
			self.baseUpdate()
			self.updateEmotions()


	def initEmotions(self):
		"""Initialise the human's wants and needs"""
		self.happiness = my.STARTINGHAPPINESS
		self.hunger = my.STARTINGHUNGER
		self.lastHunger = self.hunger
		bubblePos = (self.rect.centerx, self.rect.top - my.BUBBLEMARGIN)
		self.intention = None
		self.thought = None
		self.thoughtIsUrgent = False
		self.bubble = ThoughtBubble(self.thought, bubblePos, self.thoughtIsUrgent)


	def updateEmotions(self):
		"""Update the human's wants and needs, and kills it if need be!"""
		# HUNGER
		self.hunger -= 1
		if self.hunger < my.HUNGERWARNING or (self.thought == 'eating' and self.hunger < my.MAXHUNGER - 50):
			if not self.intention == 'find food': # ^ is hungry or eating?
				self.goGetFood()
				self.thoughtIsUrgent = False
			if self.hunger < my.HUNGERURGENT:
				self.thought = 'hungry'
				self.thoughtIsUrgent = True
		elif self.intention == 'find food': # reset values
			self.intention = None
			self.thought = None
		if self.hunger > self.lastHunger and self.intention == 'find food': # is eating?
			self.thought = 'eating'
			if self.occupation == 'builder':
				self.removeSiteReservation()
				self.building, self.destination, self.destinationSite = None, None, None
		if self.hunger < 1: # starved to death?
			self.causeOfDeath = 'starved to death'
			self.die()
		self.lastHunger = self.hunger

		# THOUGHTBUBBLE
		bubblePos = (self.rect.right + my.BUBBLEMARGIN, self.rect.top - my.BUBBLEMARGIN)
		self.bubble.update(self.thought, bubblePos, self.thoughtIsUrgent)
		if self.intention == 'working':
			self.thought = 'working'
		if self.thought == None:
			thoughtText = 'chillaxing'
		else:
			thoughtText = self.thought
		if self.thoughtIsUrgent:
			urgency = 'very '
		else: urgency = ''
		self.tooltip.text = self.name + ' is ' + urgency + thoughtText


	def goGetFood(self):
		"""Find the nearest food place and go and eat there"""
		sites = my.map.findNearestBuildings(self.coords, my.foodBuildings)
		if sites:
			site = sites[0]
			self.destination = random.choice(site.AOEcoords)
			self.intention = 'find food'
		self.thought = 'hungry'




class Builder(Human):
	"""Human that goes to constructions sites and builds them"""
	def __init__(self, coords):
		Human.__init__(self, coords, pygame.image.load('assets/mobs/builder.png'))
		self.building = None
		self.destinationSite = None
		self.occupation = 'builder'


	def update(self):
		if not self.isDead:
			#if my.tick[self.tick]:
			#	print('name %s, thought %s, building %s, intention %s' %(self.name, self.thought, self.building, self.intention))
			if self.building == None and my.tick[self.tick]:
				self.findConstructionSite()
			self.build()
			if (self.destinationSite and self.destination) or self.building:
				self.thought = 'working'
				self.intention = 'working'
			elif self.thought == 'working': # just finished work
				self.thought = None
				self.thoughtIsUrgent = False
			self.updateHuman()
			if self.intention == 'working' and (not self.destination or not self.building):
				self.intention == None
			self.lastDestination = self.destination
	

	def findConstructionSite(self):
		"""Find nearest free cell in a site and set as destination"""
		done = False
		sites = my.map.findNearestBuildings(self.coords, my.buildingsUnderConstruction)
		if sites and (self.intention == None or self.intention == 'working'):
			for site in sites:
				for x in range(len(site.buildersPositions)):
					for y in range(len(site.buildersPositions[0])):
						if done: break
						if site.buildersPositions[x][y] == None:
							# go to, and reserve a place at, the site
							self.destination = site.buildersPositionsCoords[x][y]
							site.buildersPositions[x][y] = self
							if (self.destination != self.lastDestination) or (self.intention not in 'working'):
								self.removeSiteReservation()
							self.destinationSite = site
							self.buildPosx, self.buildPosy = x, y
							done = True
						if done: break
					if done: break
				if done: break


	def removeSiteReservation(self):
		"""Removes the reserved spot at the lost construction site"""
		if self.destinationSite:
			self.destinationSite.buildersPositions[self.buildPosx][self.buildPosy] = None
			self.building = None



	def build(self):
		"""If at site, construct it. If site is done, look for a new one."""
		done = False
		for site in my.buildingsUnderConstruction:
			for x in range(len(site.buildersPositions)):
				for y in range(len(site.buildersPositions[0])):
					if done: break
					if site.buildersPositionsCoords[x][y] == self.coords:
						self.building = site
						self.destinationSite = None
						self.building.buildProgress += my.CONSTRUCTIONSPEED
						self.intention = 'working'
						done = True
					if done: break
				if done: break
		if not done:
			self.building = None
		if my.builtBuildings.has(self.building):
			self.building = None
			self.intention = None



class ThoughtBubble:
	"""A visual display of a mob's thoughts, a cloud with an icon in it."""
	bubble = pygame.image.load('assets/mobs/thoughtBubble/bubble.png').convert()
	urgentBubble = pygame.image.load('assets/mobs/thoughtBubble/urgentBubble.png').convert_alpha()
	icons = {}
	for icon in ['None', 'happy', 'sad', 'hungry', 'working']:
		icons[icon] = pygame.image.load('assets/mobs/thoughtBubble/' + icon + '.png')
	animIcons = {}
	for icon in ['eating']:
		animIcons[icon] = loadAnimationFiles('assets/mobs/thoughtBubble/' + icon, icon)

	def __init__(self, thought, pos, isUrgent=False):
		self.alpha = 200
		self.rect = pygame.Rect((0,0), (20, 20))
		self.image = None
		self.animCount = 0
		self.thought = str(thought)
		self.isUrgent = isUrgent
		self.updateSurf()
		self.update(self.thought, pos, self.isUrgent) # blit


	def updateSurf(self):
		"""Called whenever a new thought or urgency is needed"""
		if self.thought in ThoughtBubble.icons.keys():
			self.animated = False
			self.icon = ThoughtBubble.icons[self.thought]
		elif self.thought in ThoughtBubble.animIcons.keys():
			self.animated = True
			if my.ticks % 5 ==0:
				self.animCount += 1
			if self.animCount == len(ThoughtBubble.animIcons[self.thought]):
				self.animCount = 0
			self.icon = ThoughtBubble.animIcons[self.thought][self.animCount]
		if self.isUrgent:
			self.image = ThoughtBubble.urgentBubble.copy()
		else:
			self.image = ThoughtBubble.bubble.copy()
		self.image.blit(self.icon, (0,0))
		self.image.convert_alpha()


	def update(self, thought, pos, isUrgent=False):
		if self.alpha > 0:
			self.alpha -= 5
		if str(thought) != self.thought or isUrgent != self.isUrgent or self.animated:
			self.isUrgent = isUrgent
			self.thought = str(thought)
			self.alpha = 200
			self.updateSurf()
		self.image.set_alpha(self.alpha)
		self.rect.midbottom = pos
		my.surf.blit(self.image, self.rect)



class Corpse(pygame.sprite.Sprite):
	"""Eyecandy spawned when a human dies"""
	image = pygame.image.load('assets/mobs/corpse.png')
	def __init__(self, pos, livingImage, name, causeOfDeath=None):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.corpses)
		self.pos, self.name, self.causeOfDeath = pos, name, causeOfDeath
		self.animCount = 0 # count up to 90
		self.livingImage = livingImage
		self.initTooltip()

	def update(self):
		if self.animCount > -90:
			self.img = pygame.transform.rotate(self.livingImage, self.animCount)
			self.animCount -= 5
		else: self.img = Corpse.image
		my.surf.blit(self.img, self.pos)
		self.handleTooltip()


	def initTooltip(self):
		"""Initialises a tooltip that appears when the mob is hovered"""
		x, y = self.pos
		tooltipPos = (x + ui.GAP * 4, y)
		self.tooltip = ui.Tooltip(self.name + ' ' + self.causeOfDeath, tooltipPos)


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		if my.input.hoveredCell == my.map.pixelsToCell(self.pos):
			isHovered = True
		else:
			isHovered = False
		self.tooltip.simulate(isHovered, True)
