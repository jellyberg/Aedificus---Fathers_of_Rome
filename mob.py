import my, pygame, map, ui, os, random, math, shadow
from pygame.locals import *

my.allMobs = pygame.sprite.Group()
my.allHumans = pygame.sprite.Group()
my.corpses = pygame.sprite.Group()
my.designatedTrees = pygame.sprite.Group()

def updateMobs():
	for mob in my.allMobs.sprites():
		mob.handleShadow()
	for mob in my.allMobs.sprites():
		mob.update()
	for corpse in my.corpses.sprites():
		corpse.update()
	for mob in my.allMobs.sprites():
		mob.handleTooltip()
	for corpse in my.corpses.sprites():
		corpse.handleTooltip()
	if len(my.designatedTrees) > my.MAXTREESDESIGNATED:
		list(iter(my.designatedTrees))[0].remove()


def loadAnimationFiles(directory):
	"""Load images from directory into a list of surfaces"""
	animation = []
	for frame in os.listdir(directory):
		name,extension = os.path.splitext(frame)
		if extension == ".png":
			path = os.path.join(directory, frame)
			img = pygame.image.load(path).convert_alpha()
			animation.append(img)
	return animation


def blitClothes(baseAnim, clothes, swimmingMask=None):
	"""Returns a list of Surfaces, or a tuple if both clothes and swimmingMask are given as arguments"""
	if clothes: clothesImg = pygame.image.load('assets/mobs/%s.png' %(clothes))
	clothedAnim, swimAnim = [], []
	for i in range(len(baseAnim)):
		if clothes:
			frame = baseAnim[i].copy()
			frame.blit(clothesImg, (0, 0))
			clothedAnim.append(frame)
		if swimmingMask:
			if clothes:
				frame = clothedAnim[i].copy()
			else:
				frame = baseAnim[i].copy()
			frame.blit(swimmingMask, (0, 0))
			swimAnim.append(frame)
	if clothes and swimmingMask:
		return (clothedAnim, swimAnim)
	elif swimmingMask:
		return swimAnim
	else:
		return clothedAnim




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
		self.coords =  coords
		self.tick = random.randint(1, 19)
		self.initTooltip()
		self.shadow = shadow.Shadow(self, self.animation[0])


	def baseUpdate(self):
		if not self.isDead:
			self.coords =  my.map.pixelsToCell(self.rect.center)
			self.updateMove()
			self.handleImage()
			self.blit()


	def updateMove(self):
		"""Move towards self.destination coords"""
		if self.destination:
			x, y = self.rect.topleft
			destx, desty = my.map.cellsToPixels(self.destination)
			destx += my.CELLSIZE / 4
			destx = int(destx)
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
		if self.occupation == None: self.stopCarryingJob()
		elif self.occupation == 'builder': self.removeSiteReservation()
		elif self.occupation == 'woodcutter': self.stopWoodcutterJob()
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
		tooltipPos = (self.rect.right + ui.GAP, self.rect.top)
		self.tooltip = ui.Tooltip('BLANK TOOLTIP', tooltipPos)


	def handleTooltip(self):
		"""Updates a tooltip that appears when the mob is hovered"""
		self.tooltip.rect.topleft = (self.rect.right + ui.GAP, self.rect.top)
		self.tooltip.simulate(self.rect.collidepoint(my.input.hoveredPixel), True)


	def handleShadow(self):
		"""A nice shadow cast by the sun (which moves along the top of the map)"""
		self.shadow.draw(my.surf, my.sunPos)




class Human(Mob):
	"""Base class for humans, with methods for the different occupations."""
	baseAnimation = loadAnimationFiles('assets/mobs/dude')
	swimmingMask = pygame.image.load('assets/mobs/swimmingMask.png')
	swimAnim = blitClothes(baseAnimation, None, swimmingMask)
	builderAnim, builderSwimAnim = blitClothes(baseAnimation, 'builder', swimmingMask)
	buildAnim = loadAnimationFiles('assets/mobs/build')
	woodcutterAnim, woodcutterSwimAnim = blitClothes(baseAnimation, 'woodcutter', swimmingMask)
	chopAnim = loadAnimationFiles('assets/mobs/chop')

#   BASE CLASS
	def __init__(self, coords, occupation=None):
		self.occupation = occupation
		self.idleAnim = Human.baseAnimation
		if self.occupation is None:
			self.animation = self.idleAnim
		self.size = (10, 20)
		self.baseMoveSpeed = my.HUMANMOVESPEED
		self.moveSpeed = my.HUMANMOVESPEED
		if self.occupation == 'builder':
			self.initBuilder()
		elif self.occupation == 'woodcutter':
			self.initWoodcutter()
		Mob.__init__(self, self.baseMoveSpeed, self.animation, coords, self.size)
		self.name = random.choice(my.FIRSTNAMES) + ' ' + random.choice(my.LASTNAMES)
		self.tooltip.text = self.name
		self.initEmotions()
		self.carrying = None
		self.destinationItem = None
		self.destinationSite = None


	def update(self):
		if not self.isDead:
			self.baseUpdate()
			self.updateEmotions()
			if self.occupation is None:
				self.updateSerf()
			if self.occupation == 'builder':
				self.updateBuilder()
			if self.occupation == 'woodcutter':
				self.updateWoodcutter()
			if self.rect.collidepoint(my.input.hoveredPixel) and my.input.mousePressed == 2:
				self.occupation = 'woodcutter'
				self.initWoodcutter()
			if my.map.cellType(self.coords) == 'water' and self.animation == self.idleAnim:
				self.animation = self.swimAnim
			elif my.map.cellType(self.coords) != 'water' and self.animation == self.swimAnim:
				self.animation = self.idleAnim


	def initEmotions(self):
		"""Initialise the human's wants and needs"""
		self.happiness = my.STARTINGHAPPINESS
		self.hunger = my.STARTINGHUNGER + random.randint(-100, 100)
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
		if self.hunger < my.HUNGERWARNING:
			if not self.intention == 'find food': # ^ is hungry or eating?
				self.goGetFood()
				self.thoughtIsUrgent = False
			if self.hunger < my.HUNGERURGENT:
				self.thought = 'hungry'
				self.thoughtIsUrgent = True
		elif self.thought == 'eating' and self.hunger > my.FULLMARGIN and self.destination is None:
			x, y = self.coords # move away from food zone
			self.destination = (x + random.randint(3, 5), y + random.randint(2, 4))
			self.intention = None
			self.thought = None
		if self.hunger < 1: # starved to death?
			self.causeOfDeath = 'starved to death'
			self.die()
		self.lastHunger = self.hunger

		# THOUGHTBUBBLE
		bubblePos = (self.rect.left + ui.GAP, self.rect.top - my.BUBBLEMARGIN)
		self.bubble.update(self.thought, bubblePos, self.thoughtIsUrgent)
		if self.intention == 'working':
			self.thought = 'working'
		if self.thought is None:
			thoughtText = 'chillaxing'
		else:
			thoughtText = self.thought
		if self.thoughtIsUrgent:
			urgency = 'very '
		else: urgency = ''
		self.tooltip.text = self.name + ' is ' + urgency + thoughtText


	def goGetFood(self, specificSite=None):
		"""Find the nearest food place wiht slots and go and eat there. If specificSite, go there instead"""
		site = None
		if not specificSite:
			sites = my.map.findNearestBuildings(self.coords, my.foodBuildingsWithSpace)
			if sites:
				site = sites[0]
		elif specificSite:
			site = specificSite
		if site:
			self.destination = random.choice(site.AOEcoords)
			self.intention = 'find food'
			self.thought = 'hungry'
			self.stopJob()


	def changeOccupation(self, newOccupation):
		"""Change occupation and stop any previous jobs"""
		self.stopJob()
		self.occupation = newOccupation


	def stopJob(self):
		"""Stop the current job, for any occupation"""
		if self.intention == 'working':
			self.intention, self.thought, self.destination = None, None, None
		if self.occupation is None:
			self.stopCarryingJob()
		if self.occupation == 'builder':
			self.removeSiteReservation()
			self.building, self.destinationSite = None, None
		elif self.occupation == 'woodcutter':
			self.stopWoodcutterJob()


#   SERF
	def updateSerf(self):
		"""A human without an occupation who carries items around"""
		if not self.carrying:
			self.findItem()
		if self.carrying:
			self.tooltip.text += ' and carrying %s %s' %(self.carrying.quantity, self.carrying.name)
			self.carry()


	def findItem(self):
		if self.intention in [None, 'working']: # find item
			done = False
			items = my.map.findNearestBuildings(self.coords, my.itemsOnTheFloor)
			if items:
				for item in items:
					if not item.reserved and len(my.storageBuildingsWithSpace) > 0:
						self.destination = item.coords
						self.destinationItem = item
						item.reserved = self
						self.intention = 'working'
						done = True
					if done: break
		if self.destinationItem and self.coords == self.destinationItem.coords\
										 and self.destinationItem.reserved == self: # pick up item
			self.carrying = self.destinationItem
			self.destinationItem = None
			self.carrying.beingCarried = True


	def carry(self):
		if self.intention in [None, 'working'] and not self.destinationSite:
			sites = my.map.findNearestBuildings(self.coords, my.storageBuildingsWithSpace)
			done = False
			for site in sites:
				if site.totalStored + self.carrying.quantity < site.storageCapacity:
					self.intention = 'working'
					self.destinationSite = site
					self.destination = self.destinationSite.coords
				if done: break
			if not self.destinationSite:
				self.intention = None
				self.stopCarryingJob()
		# STORE ITEM
		if self.destinationSite and self.coords == self.destinationSite.coords:
			self.destinationSite.storeResource(self.carrying.name, self.carrying.quantity)
			self.carrying.kill()
			self.stopCarryingJob()


	def stopCarryingJob(self):
		if self.destinationItem:
			self.destinationItem.reserved = None
			self.destinationItem = None
		self.destinationSite = None
		if self.carrying:
			self.carrying.reserved = None
			self.carrying.coords = self.coords
			self.carrying.beingCarried = False
			self.carrying = None


#	BUILDER
	def initBuilder(self):
		"""Finds the nearest construction site and constructs it."""
		self.idleAnim = Human.builderAnim
		self.swimAnim = Human.builderSwimAnim
		self.animation = self.idleAnim
		self.destination = None
		self.building = None
		self.destinationSite = None
		self.lastDestination = None


	def updateBuilder(self):
		if not self.isDead:
			if self.building is None and my.tick[self.tick]:
				self.findConstructionSite()
			self.build()
			if self.destinationSite and my.builtBuildings.has(self.destinationSite):
				self.removeSiteReservation()
				self.destination = None
				self.intention = None
			if (self.destinationSite and self.destination) or self.building:
				self.thought = 'working'
				self.intention = 'working'
			elif self.thought == 'working': # just finished work
				self.thought = None
				self.thoughtIsUrgent = False
			if self.intention == 'working' and (not self.destination or not self.building):
				self.intention is None
			self.lastDestination = self.destination


	def findConstructionSite(self):
		"""Find nearest free cell in a site and set as destination"""
		done = False
		sites = my.map.findNearestBuildings(self.coords, my.buildingsUnderConstruction)
		if sites and (self.intention is None or self.intention == 'working'):
			for site in sites:
				for x in range(len(site.buildersPositions)):
					for y in range(len(site.buildersPositions[0])):
						if done: break
						if site.buildersPositions[x][y] is None:
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
			if self.animation != self.idleAnim:
				self.animation = self.idleAnim
				self.animFrame = 0
			self.building = None
		else:
			if self.animation != Human.buildAnim:
				self.animation = Human.buildAnim
				self.animFrame = 0
		if my.builtBuildings.has(self.building):
			self.building = None
			self.intention = None


#	WOODCUTTER
	def initWoodcutter(self):
		"""Chops down the nearest tree in my.designatedTrees"""
		self.occupation = 'woodcutter'
		self.idleAnim = Human.woodcutterAnim
		self.swimAnim = Human.woodcutterSwimAnim
		self.animation = self.idleAnim
		self.chopping = False
		self.destinationSite = None
		self.lastSite = self.destinationSite


	def updateWoodcutter(self):
		if self.intention in [None, 'working'] and not self.chopping \
								and my.resources['wood'] < my.maxResources['wood'] and my.tick[self.tick]:
			self.intention = 'working'
			self.findDestination()
		if self.destinationSite and self.coords == self.destinationSite.coords:
			self.chopping = True
			self.destinationSite.chop()
			if self.destinationSite.isDead:
				self.destinationSite = None
				self.intention, self.thought = None, None
				self.chopping = False
		else:
			self.chopping = False
			if self.animation != self.idleAnim:
				self.animation = self.idleAnim
				self.animFrame = 0
		if self.chopping:
			self.animation = Human.chopAnim
		self.lastSite = self.destinationSite


	def findDestination(self):
		"""Find nearest unreserved tree and go there"""
		if my.designatedTrees:
			self.thought = 'working'
			sites = my.map.findNearestBuildings(self.coords, my.designatedTrees)
			if sites:
				done = False
				for site in sites:
					if not site.reserved or site.reserved == self:
						self.destinationSite = site
						self.destination = self.destinationSite.coords
						self.destinationSite.reserved = self
						if self.lastSite and self.lastSite != self.destinationSite:
							self.lastSite.reserved = False
						done = True
					if done: return
		self.thought = None
		self.intention = None


	def stopWoodcutterJob(self):
		if self.destinationSite:
			self.destinationSite.reserved = False
			self.destinationSite = None
		self.chopping = False


#   FISHERMAN
#	def initFisherman(self):
#		self.




class ThoughtBubble:
	"""A visual display of a mob's thoughts, a cloud with an icon in it."""
	bubble = pygame.image.load('assets/mobs/thoughtBubble/bubble.png').convert()
	urgentBubble = pygame.image.load('assets/mobs/thoughtBubble/urgentBubble.png').convert_alpha()
	icons = {}
	for icon in ['None', 'happy', 'sad', 'hungry', 'working']:
		icons[icon] = pygame.image.load('assets/mobs/thoughtBubble/' + icon + '.png')
	animIcons = {}
	for icon in ['eating']:
		animIcons[icon] = loadAnimationFiles('assets/mobs/thoughtBubble/' + icon)

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
