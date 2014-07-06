# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import pygame, my, math, random, time, building, mob, sound

my.selectionBoxGroup = pygame.sprite.GroupSingle()
my.demolisher = pygame.sprite.GroupSingle()
my.UItips = pygame.sprite.Group()
my.ongoingUItipTexts = []
my.pulseLights = pygame.sprite.Group()
my.moveMarkers = pygame.sprite.Group()
my.buildingMenus = pygame.sprite.Group()

BASICFONT = pygame.font.Font('assets/fonts/roboto medium.ttf', 14)
MEDIUMFONT =pygame.font.Font('assets/fonts/roboto regular.ttf', 16)
BIGFONT   = pygame.font.Font('assets/fonts/roboto regular.ttf', 20)
MEGAFONT  = pygame.font.Font('assets/fonts/roboto regular.ttf', 42)
GAP = 5
TOOLTIPWORDSPERLINE = 6  # subtract 1!

def genText(text, topLeftPos, colour, font=BASICFONT):
	surf = font.render(text, 1, colour)
	rect = surf.get_rect()
	rect.topleft = topLeftPos
	return (surf, rect)


def resourceText(text, topLeftPos):
	"""Generates and blits resource amount indicators"""
	x, y = topLeftPos
	textSurf, textRect = genText(text.capitalize(), (GAP, GAP), my.WHITE, BASICFONT)
	bgRect = pygame.Rect((x, y), (textRect.width + GAP * 2, textRect.height + GAP * 2))
	bgSurf = pygame.Surface((bgRect.width, bgRect.height))
	bgSurf.fill(my.BROWN)
	bgSurf.blit(textSurf, textRect)
	my.screen.blit(bgSurf, bgRect)
	return bgRect.width


def handleTooltips():
	for site in my.allBuildings:
		site.handleTooltip()
	for corpse in my.corpses:
		corpse.handleTooltip()
	for mob in my.allMobs:
		if mob not in my.allEnemies:
			mob.handleTooltip()


def updateUItips():
	"""Handles UI tip updating and dismissing"""
	for tip in my.UItips:
		tip.update(tip.text not in my.ongoingUItipTexts)
	my.ongoingUItipTexts = []



class Hud:
	"""Handles resource amounts, buttons and tooltips"""
	def __init__(self):
		self.buttons = []
		self.tooltips = []
		self.HIGHLIGHTS = {}
		for colour in Highlight.IMGS.keys():
			self.HIGHLIGHTS[colour] = Highlight(colour)

		self.bottomBar = BottomBar()
		self.missionBar = MissionProgressBar()
		self.occupationAssigner = OccupationAssigner()
		self.designator = Designator()
		self.minimap = Minimap()
		self.selectionButtons = SelectionButtons(self.minimap)
		self.statusArea = StatusArea()

		my.surf = pygame.Surface(my.map.surf.get_size())
		self.regenSurf = False


	def updateHUD(self, dt):
		"""Updates elements that are blitted to screen"""
		self.bottomBar.update()
		self.missionBar.update()
		self.occupationAssigner.update()
		self.designator.update()
		self.selectionButtons.update(dt)
		self.minimap.update()
		self.statusArea.update()
		updateUItips()
		# RESOURCE AMOUNTS
		i = 0
		currentWidth = 0
		for resource in my.RESOURCENAMEORDER:
			currentWidth += resourceText('%s: %s' % (resource, my.resources[resource]), (GAP * (i + 1) + currentWidth, GAP))
			i += 1


	def updateWorldUI(self):
		"""Updates elements that are blitted to my.surf"""
		# HIGHLIGHT
		if my.mode != 'build' and my.input.hoveredCell:
			if my.selectedTroops:
				currentHighlight = self.HIGHLIGHTS['red']
			elif my.mode == 'look':
				if my.input.hoveredCellType not in ['grass', 'water', 'rock']:
					currentHighlight = self.HIGHLIGHTS['yellow']
				else:
					currentHighlight = self.HIGHLIGHTS['blue']
			currentHighlight.update(my.input.hoveredCell)
		# SELECTION BOX
		if my.input.mousePressed == 1 and not my.selectionBoxGroup.sprite:
			if my.designationMode == 'tree':
				SelectionBox('trees', False, False)
			elif my.designationMode == 'ore':
				SelectionBox(False, 'ores', False)
			elif my.designationMode == None:
				SelectionBox(False, False, 'soldiers')
		if my.selectionBoxGroup.sprite:
			my.selectionBoxGroup.sprite.update()
		my.pulseLights.update()
		my.moveMarkers.update()
		my.demolisher.update()
		# BUILDING MENUS
		for menu in my.buildingMenus.sprites():
			menu.update()


	def genSurf(self):
		"""Regenerates my.surf next frame to prevent blank frames"""
		#self.regenSurf = True
		self.genBlankSurf()


	def genBlankSurf(self):
		"""Regenerates my.surf"""
		my.surf = pygame.Surface(my.map.surf.get_size())
		my.hud.updateWorldUI()



class Button:
	"""A simple button, can be clickable, can have tooltip. When clicked, self.isClicked=True"""
	def __init__(self, text, style, screenPos, isClickable=0, isTitle=0, screenPosIsTopRight=0, tooltip=None):
		"""style is redundant atm, tooltip should be a string"""
		self.text, self.style, self.screenPos, self.isClickable, self.posIsTopRight = \
		(text, style, screenPos, isClickable, screenPosIsTopRight)
		if isTitle == 1:
			self.textSurf = BIGFONT.render(self.text, 1, my.LIGHTGREY)
		elif isTitle == 2:
			self.textSurf = MEGAFONT.render(self.text, 1, my.LIGHTGREY)
		else:
			self.textSurf = BASICFONT.render(self.text, 1, my.WHITE)
		# CREATE BASIC SURF
		self.padding = 10 # might be controlled by 'style' eventually
		self.buttonSurf = pygame.Surface((self.textSurf.get_width() + self.padding,
										  self.textSurf.get_height() + self.padding))
		self.buttonSurf.fill(my.BROWN)
		self.buttonSurf.blit(self.textSurf, (int(self.padding /2), int(self.padding /2)))
		self.currentSurf = self.buttonSurf
		self.rect = pygame.Rect(self.screenPos, self.buttonSurf.get_size())
		if self.posIsTopRight:
			self.rect.topright = self.screenPos
		else:
			self.rect.topleft = self.screenPos
		# CREATE ADDITIONAL SURFS
		if isClickable:
			# MOUSE HOVER
			self.hoverSurf = pygame.Surface(self.buttonSurf.get_size())
			self.hoverSurf.fill(my.DARKBROWN)
			self.hoverSurf.blit(self.textSurf, (int(self.padding /2), int(self.padding /2)))
			# MOUSE CLICK
			self.clickSurf = pygame.Surface(self.buttonSurf.get_size())
			self.clickSurf.fill(my.BROWNBLACK)
			self.clickSurf.blit(self.textSurf, (int(self.padding /2), int(self.padding /2)))
			self.isClicked = False
			self.isHovered = False
		self.hasTooltip = False
		if tooltip:
			self.hasTooltip = True
			self.tooltip = Tooltip(tooltip, (self.rect.right + GAP, self.rect.top))

	def simulate(self, userInput):
		if self.isClickable or self.hasTooltip: self.handleClicks(userInput)
		if self.hasTooltip: self.tooltip.simulate(self.isHovered)
		my.screen.blit(self.currentSurf, self.rect)

	def handleClicks(self, userInput=None):
		self.isClicked = False
		wasHovered = self.isHovered
		self.isHovered = False
		if self.rect.collidepoint(my.input.mousePos):
			if userInput.mousePressed == 1:
				self.currentSurf = self.clickSurf
			else:
				if not wasHovered:
					sound.play('tick', 0.8, False)
				self.currentSurf = self.hoverSurf
				self.isHovered = True
		else:
			self.currentSurf = self.buttonSurf
		if userInput.mouseUnpressed == True and self.rect.collidepoint(my.input.mousePos):
			self.isClicked = True
			sound.play('click', 0.8, False)



class Tooltip:
	"""A multiline text box, displayed when isHovered=True"""
	def __init__(self, text, pos, font=BASICFONT, colour=my.CREAM, arrowSide='left'):
		self.pos, self.text, self.font, self.colour, self.arrowSide = pos, text, font, colour, arrowSide
		self.alpha = 0
		self.newTooltip()
		self.lastText = self.text
		self.lockAlpha = False
		self.fadeRate = 20


	def newTooltip(self):
		# GET TEXT OBJS
		self.textObjs, self.textHeight = self.genTextObjs(self.text)
		self.textWidth = self.getLongestTextLine(self.textObjs)
		# CREATE SURF
		self.surf = pygame.Surface((self.textWidth + GAP * 3, self.textHeight + GAP * 2))

		width, height = self.surf.get_width(), self.surf.get_height()
		if self.arrowSide == 'left':
			pygame.draw.rect(self.surf, self.colour, (GAP, 0, width - GAP, height))
			pygame.draw.polygon(self.surf, self.colour, [(0, 10), (GAP, 5), (GAP, 15)])

		elif self.arrowSide == 'right':
			pygame.draw.rect(self.surf, self.colour, (0, 0, width - GAP, height))
			pygame.draw.polygon(self.surf, self.colour, [(width, 10), (width - GAP, 5), (width - GAP, 15)])

		for i in range(len(self.textObjs)):
			self.surf.blit(self.textObjs[i][0], self.textObjs[i][1])

		self.surf.set_colorkey(my.BLACK)
		try:
			oldPos = self.rect.topleft
		except: pass
		self.rect = self.surf.get_rect()
		try: 
			self.rect.topleft = oldPos
		except:
			self.rect.topleft = self.pos			
		self.needNewSurf = False
		

	def simulate(self, isHovered, blitToLand=False):
		if self.text != self.lastText:
			self.needNewSurf = True
		if self.alpha > 0 and self.needNewSurf:
			self.newTooltip()

		if isHovered and self.text != 'BLANK TOOLTIP':
			if self.alpha < 200: self.alpha += 20
		elif self.alpha > 0 and not self.lockAlpha:
			self.alpha -= self.fadeRate

		if self.alpha > 0:
			self.surf.set_alpha(self.alpha)
			if not blitToLand:
				my.screen.blit(self.surf, self.rect)
			if blitToLand:
				my.surf.blit(self.surf, self.rect)
		self.lastText = self.text


	def genTextObjs(self, text):
		wordList = text.split()
		extraWords = wordList[:]
		numLines = int(math.ceil(len(wordList) / TOOLTIPWORDSPERLINE))
		newText = [] # a list of strings, each line having one string
		textObjs = [] # a list of two item lists, each list having a surf and rect object for a line
		# GENERATE LIST OF STRINGS
		for lineNum in range(0, numLines-1):
			line = ''
			for wordNum in range(0, TOOLTIPWORDSPERLINE):
				currentWord = wordList[lineNum * (TOOLTIPWORDSPERLINE) + wordNum]
				line = line + currentWord + ' '
				extraWords.remove(currentWord)
			newText.append(line)
		lastLine = ' '.join(extraWords)
		newText.append(lastLine)
		# CONVERT STRINGS TO TEXT SURFS AND RECTS
		testText, testRect = genText('This is a test', (0, 0), my.BLACK, self.font)
		textHeight = testText.get_height()
		totalHeight = textHeight * (len(newText)) + GAP * (len(newText))
		for lineNum in range(len(newText)):
			surf, rect = genText(newText[lineNum], (GAP * 2, textHeight * lineNum + GAP * lineNum + GAP),
								 my.DARKGREY, self.font)
			textObjs.append([surf, rect])
		return textObjs, totalHeight


	def getLongestTextLine(self, textObjs):
		longestLineWidth = 0
		for i in range(len(textObjs)):
			if textObjs[i][1].width > longestLineWidth:
				longestLineWidth = textObjs[i][1].width
		return longestLineWidth



class Slider:
	"""A slider looking thing that allows for selection of numbers in a specified range"""
	size = (200, 80)
	pointerImg = pygame.image.load('assets/ui/pointer.png').convert_alpha()
	pointerHoverImg = pygame.image.load('assets/ui/pointerHover.png').convert_alpha()

	def __init__(self, pos, rangeVals, label, defaultNum, barColour=my.PASTELBLUE, bgColour=my.SKYBLUE):
		self.min, self.max = rangeVals # tuple of minimum and maximum values the slider can output
		assert self.min < self.max and self.min != self.max, 'Slider range values are invalid'
		assert self.min <= defaultNum <= self.max, 'Slider default num is invalid'
		self.range = self.max - self.min

		self.label = label # describe what the slider is changing
		self.barColour, self.bgColour = barColour, bgColour

		self.rect = pygame.Rect((pos[0], pos[1]), Slider.size)
		self.genSurf()
		self.pointerRect.midbottom = ((defaultNum - self.min) / float(self.range) * self.rect.width, 45)

		self.currentlyClicked = False
		self.wasHovered = False

		self.lastNum = -1 # always update number text on first update loop 
		self.lastNumRect = None




	def update(self):
		"""Renders the slider, changes self.pointerRect based on input, returns the pointer value"""
		self.surf.blit(self.baseSurf, (0, 0))
		self.surf.blit(Slider.pointerImg, self.pointerRect)

		if my.input.mousePressed != 1: self.currentlyClicked = False

		if self.currentlyClicked or self.globalBarRect.collidepoint(my.input.mousePos) or self.pointerRectGlobal.collidepoint(my.input.mousePos):
			if not self.wasHovered: sound.play('tick', 0.8, False)
			self.wasHovered = True
			self.surf.blit(Slider.pointerHoverImg, self.pointerRect)
			if my.input.mousePressed == 1:
				self.currentlyClicked = True
				self.surf.blit(Slider.pointerHoverImg, self.pointerRect)

				if 0 < (my.input.mousePos[0] - self.globalBarRect.x) < self.globalBarRect.width:
					self.pointerRect.x = my.input.mousePos[0] - self.globalBarRect.x
				elif 0 > (my.input.mousePos[0] - self.globalBarRect.x):
					self.pointerRect.x = self.barRect.left
				elif (my.input.mousePos[0] - self.globalBarRect.x) > self.globalBarRect.width:
					self.pointerRect.right = self.barRect.right

				self.pointerRectGlobal = self.globaliseRect(self.pointerRect)

		else: self.wasHovered = False

		sliderValue = int(self.min + self.pointerRect.x / float(self.rect.width) * self.range)

		if sliderValue != self.lastNum:
			self.updateNumText(sliderValue)

		my.screen.blit(self.surf, self.rect)
		return sliderValue



	def genSurf(self):
		"""Generate a new slider baseSurf and rects, with labels"""
		self.baseSurf = pygame.Surface(Slider.size)
		self.surf = pygame.Surface(self.baseSurf.get_size())
		if self.bgColour:
			self.baseSurf.fill(self.bgColour)
		else:
			self.baseSurf.set_colorkey(my.COLOURKEY)
			self.baseSurf.fill(my.COLOURKEY)

		self.barRect = pygame.Rect((GAP, 40), (190, 10))
		self.globalBarRect = self.globaliseRect(self.barRect)
		pygame.draw.rect(self.baseSurf, self.barColour, self.barRect)

		self.pointerRect = Slider.pointerImg.get_rect()
		self.pointerRectGlobal = self.globaliseRect(self.pointerRect)

		# GENERATE THE TEXT LABEL, USING THE BIGGEST FONT THAT FITS
		titleSurf, titleRect = genText(self.label, (GAP, 2), my.WHITE, BIGFONT)
		if titleRect.width > self.rect.width - GAP:
			titleSurf, titleRect = genText(self.label, (GAP, 2), my.WHITE, MEDIUMFONT)
		if titleRect.width > self.rect.width - GAP:
			titleSurf, titleRect = genText(self.label, (GAP, 2), my.WHITE, BASICFONT)
		self.baseSurf.blit(titleSurf, titleRect)


	def updateNumText(self, num):
		"""Updates the text showing the current selected value of the slider"""
		if self.lastNumRect:
			self.baseSurf.fill(self.bgColour, self.lastNumRect)

		numSurf, numRect = genText(str(num), (0, 0), my.WHITE, BIGFONT)
		numRect.bottomright = (180, 80)
		self.baseSurf.blit(numSurf, numRect)

		self.lastNum = num
		self.lastNumRect = numRect


	def globaliseRect(self, localRect):
		"""Returns a new rect with the Slider's topleft coords added on to the rect's coords"""
		return pygame.Rect((localRect.x + self.rect.x, localRect.y + self.rect.y), localRect.size)



class BottomBar:
	"""A multi-tab (only 1 tab is used atm) menu at the bottom of the screen which allows contruction of buildings"""
	height = 50
	margin = 14 # at left hand side
	cell   = 52 # width
	def __init__(self):
		self.bounds = pygame.Rect((GAP * 2, my.WINDOWHEIGHT - BottomBar.height - GAP * 4), (BottomBar.margin + BottomBar.cell * 12, BottomBar.height))
		self.tab = 0
		self.cellBackgrounds = []

		bgImg = pygame.image.load('assets/ui/bottomBar/cellBg.png')
		flippedBgImg = pygame.transform.flip(bgImg, 1, 1)
		for i in range(0, 360, 90):
			self.cellBackgrounds.append(pygame.transform.rotate(bgImg, i))
			self.cellBackgrounds.append(pygame.transform.rotate(flippedBgImg, i))
		self.cellHighlight = pygame.image.load('assets/ui/bottomBar/cellHighlight.png').convert_alpha()
		self.cellClick     = pygame.image.load('assets/ui/bottomBar/cellClick.png').convert_alpha()
		self.lockImg       = pygame.image.load('assets/ui/padlock.png').convert_alpha()

		self.genRects()
		self.genBackgroundImg()
		self.clickedCell, self.hovered, self.lastClicked, self.lastHovered = None, None, None, None
		self.surf = pygame.Surface(self.bounds.size)
		self.surf.blit(self.backgroundImg, (0, 0))
		self.surf.set_colorkey(my.BLACK)
		self.genTooltips()
		self.lastUnlockedBuildings = my.unlockedBuildings[:]

		stats = my.BUILDINGSTATS
		self.imgsForGenSurf = [stats['hut']['img'], stats['shed']['img'],
					  stats['orchard']['img'], stats['fishing boat']['img'], stats['fish mongers']['img'],
					  stats['pool']['img'], stats['blacksmith']['img'], stats['town hall']['img']]
		self.SURFS = [self.genSurf(self.imgsForGenSurf)]
		self.surf.blit(self.SURFS[self.tab], (0, 0))



	def genRects(self):
		"""Generates a list of twelve rects, to be used for collision detection with the mouse"""
		self.localRects = []
		self.globalRects = []
		for i in range(12):
			self.localRects.append(pygame.Rect((BottomBar.margin + i * BottomBar.cell, 0), 
								   (BottomBar.cell, BottomBar.cell)))
			self.globalRects.append(pygame.Rect((BottomBar.margin + i * BottomBar.cell, self.bounds.top), 
									(BottomBar.cell, BottomBar.cell)))


	def genBackgroundImg(self):
		"""Generates a background image for the bottom bar"""
		self.backgroundImg = pygame.Surface(self.bounds.size)
		self.backgroundImg.set_colorkey(my.BLACK)
		for rect in self.localRects:
			self.backgroundImg.blit(random.choice(self.cellBackgrounds), rect)


	def genSurf(self, imgs):
		"""Generate a new surface with the imgs passed blitted onto it. These can be reused"""
		surf = self.backgroundImg.copy()
		assert len(imgs) <= 12, "Too many images for bottom bar!"
		for i in range(len(imgs)):
			# scale and blit preview image to BottomBar cell
			width, height = imgs[i].get_rect().size
			if width > height:
				widthScale = 40
				heightScale = int(float(height) / width * 40)
			else:
				heightScale = 40
				widthScale = int(float(width) / height * 40)
			img = pygame.transform.scale(imgs[i], (widthScale, heightScale))
			imgRect = img.get_rect()
			imgRect.center = self.localRects[i].center
			surf.blit(img, imgRect)

		lockRect = self.lockImg.get_rect()
		for i in range(len(my.BUILDINGNAMES)):
			if my.BUILDINGNAMES[i] not in my.unlockedBuildings:
				lockRect.center = self.localRects[i].center
				surf.blit(self.lockImg, lockRect)

		img = pygame.image.load('assets/ui/bomb.png')
		imgRect = img.get_rect()
		imgRect.center = self.localRects[-1].center
		surf.blit(img, imgRect)

		return surf


	def genTooltips(self):
		self.tooltips = []
		for i in range(len(my.BUILDINGSTATS)):
			site = my.BUILDINGSTATS[my.BUILDINGNAMES[i]]
			text = '%s: %s Building materials needed: %s' \
					%(my.BUILDINGNAMES[i].upper(), site['description'], site['buildMaterials'])
			x = self.globalRects[i].right
			x += GAP
			tooltip = Tooltip(text, (x, 0))
			tooltip.rect.bottom = my.WINDOWHEIGHT - GAP
			self.tooltips.append(tooltip)


	def update(self):
		if my.unlockedBuildings != self.lastUnlockedBuildings:
			self.SURFS[self.tab] = self.genSurf(self.imgsForGenSurf)

		self.handleInput()
		if self.clickedCell != None and not my.selectionBoxGroup:
			if self.clickedCell == 0 and 'hut' in my.unlockedBuildings:
				building.Hut()
			elif self.clickedCell == 1 and 'shed' in my.unlockedBuildings:
				building.Shed()
			elif self.clickedCell == 2 and 'orchard' in my.unlockedBuildings:
				building.Orchard()
			elif self.clickedCell == 3 and 'fishing boat' in my.unlockedBuildings:
				building.FishingBoat()
			elif self.clickedCell == 4 and 'fish mongers' in my.unlockedBuildings:
				building.FishMongers()
			elif self.clickedCell == 5 and 'pool' in my.unlockedBuildings:
				building.Pool()
			elif self.clickedCell == 6 and 'blacksmith' in my.unlockedBuildings:
				building.Blacksmith()
			elif self.clickedCell == 7 and 'town hall' in my.unlockedBuildings:
				building.TownHall()
			elif self.clickedCell == 11:
				Demolisher()
			else:
				sound.play('error', 0.4, False)
		my.screen.blit(self.surf, self.bounds)

		i=0
		for tooltip in self.tooltips:
			if self.hovered == i: hovered = True
			else: hovered = False
			tooltip.simulate(hovered)
			i += 1

		self.lastUnlockedBuildings = my.unlockedBuildings[:]


	def handleInput(self):
		"""Update surf highlights and self.hovered and self.clickedCell"""
		self.clickedCell = None
		self.hovered = None
		resetted = False
		if self.bounds.collidepoint(my.input.mousePos):
			for i in range(len(self.globalRects)):
				rect = self.globalRects[i]
				if rect.collidepoint(my.input.mousePos):
					self.hovered = i
			if (self.hovered != self.lastHovered) or (self.clickedCell != self.lastClicked):
				# reset surf if hover or click is finished
				self.surf = self.SURFS[self.tab].copy()
				resetted = True
				if self.hovered != self.lastHovered and self.hovered is not None:
					sound.play('tick', 0.8, False)
			for i in range(len(self.globalRects)):
				rect = self.globalRects[i]
				if rect.collidepoint(my.input.mousePos):
					# hovered
					if (self.lastHovered is None or resetted):
						self.surf.blit(self.cellHighlight, self.localRects[i])
					if my.input.mousePressed == 1 and (self.lastClicked is None or resetted): # clicked
						self.surf.blit(self.cellClick, self.localRects[i])
					if my.input.mouseUnpressed == 1:
						self.clickedCell = i
						sound.play('click', 0.8, False)
			self.lastClicked, self.lastHovered = self.clickedCell, self.hovered
		else:
			self.surf = self.SURFS[self.tab].copy()



class Designator:
	"""A menu to select the kind of SelectionBox created when RMB is pressed. Can be collapsed when the icon is clicked"""
	def __init__(self):
		my.designationMode = None
		self.baseSurf = pygame.image.load('assets/ui/designator/background.png')
		self.surf = self.baseSurf.copy()
		self.COLLAPSEDTOPLEFT = (my.WINDOWWIDTH - 10, int(my.WINDOWHEIGHT / 5))
		self.OPENTOPLEFT      = (my.WINDOWWIDTH - self.surf.get_width() - GAP * 4, int(my.WINDOWHEIGHT / 5))
		self.rect = self.surf.get_rect()
		self.rect.topleft = self.OPENTOPLEFT
		self.tabRect = pygame.Rect((self.rect.left, self.rect.top + 12), (10, 50))

		self.selected = pygame.image.load('assets/ui/designator/selected.png')
		self.highlight = pygame.image.load('assets/ui/designator/hover.png')
		self.tabHighlight = pygame.image.load('assets/ui/designator/tabHover.png')
		self.tabHoveredSurf = self.baseSurf.copy()
		self.tabHoveredSurf.blit(self.tabHighlight, (0, 0))
		self.collapsed = False
		self.animate = None
		self.lastHovered = None

		self.buttonRects = []
		x, y = self.OPENTOPLEFT
		for i in range(y, y + 100, 50):
			self.buttonRects.append(pygame.Rect((x + 10, i), (50, 50)))


	def update(self):
		#self.handleTab()
		my.screen.blit(self.surf, self.rect)
		if self.collapsed == False and not self.animate:
			self.handleButtons()


	def handleTab(self):
		"""Opens or collapses the designator's tab when the icon is clicked"""
		# OPEN TAB
		self.tabRect.topleft = (self.rect.left, self.rect.top + 12)
		if self.collapsed and self.animate is None:
			if self.tabRect.collidepoint(my.input.mousePos):
				self.surf = self.tabHoveredSurf
				if my.input.mousePressed == 1:
					self.collapsed = False
					self.animate = 'open'
					self.surf = self.baseSurf
					sound.play('click', 0.8, False)
			else:
				self.surf = self.baseSurf
		# COLLAPSE TAB
		elif not self.collapsed and self.animate is None:
			if self.tabRect.collidepoint(my.input.mousePos):
				self.surf = self.tabHoveredSurf
				if my.input.mousePressed == 1:
					self.collapsed = True
					self.animate = 'close'
					self.surf = self.baseSurf
					sound.play('click', 0.8, False)
			else:
				self.surf = self.baseSurf
		# ANIMATE
		if self.animate == 'open':
			if self.rect.topleft == self.OPENTOPLEFT:
				self.animate = None
			else:
				self.rect.x -= 5
		elif self.animate == 'close':
			if self.rect.topleft == self.COLLAPSEDTOPLEFT:
				self.animate = None
			else:
				self.rect.x += 5


	def handleButtons(self):
		"""If a button (tree or ore) is clicked, change designation mode"""
		if my.designationMode:
			if my.designationMode == 'tree':
				selectedRect = self.buttonRects[0]
			elif my.designationMode == 'ore':
				selectedRect = self.buttonRects[1]
			my.screen.blit(self.selected, selectedRect)
		if self.rect.collidepoint(my.input.mousePos):
			i = 0
			for rect in self.buttonRects:
				if rect.collidepoint(my.input.mousePos):

					my.screen.blit(self.highlight, rect)
					if rect != self.lastHovered:
						sound.play('tick', 0.8, False)
					self.lastHovered = rect

					if my.input.mousePressed == 1:
						my.screen.blit(self.highlight, rect)

					if my.input.mouseUnpressed == 1:
						if i == 0:
							if my.designationMode == 'tree':
								my.designationMode = None
							else:
								my.designationMode = 'tree'
						elif i == 1:
							if my.designationMode == 'ore':
								my.designationMode = None
							else:
								my.designationMode = 'ore'
						sound.play('click', 0.8, False)
				i += 1



class OccupationAssigner:
	"""A dialogue box to +/- the number of each occupation"""
	IMGS = {}
	for name in ['background', 'plus', 'plusHover', 'plusClick', 'minus', 'minusHover', 'minusClick']:
		IMGS[name] = pygame.image.load('assets/ui/occupationAssigner/%s.png' %(name)).convert_alpha()
	OCCUPATIONIMGS = [mob.Human.idleAnimation[0], mob.Human.builderIdleAnim[0], mob.Human.woodcutterIdleAnim[0],
					  mob.Human.minerIdleAnim[0], mob.Human.fishermanIdleAnim[0], mob.Human.blacksmithIdleAnim[0],
					  mob.Human.soldierIdleAnim[0]]
	MAXCOLUMNS = 3
	def __init__(self):
		self.leftx = my.WINDOWWIDTH - OccupationAssigner.IMGS['background'].get_width() - GAP * 4
		self.topy = int(my.WINDOWHEIGHT / 2)
		self.rect = pygame.Rect((self.leftx, self.topy), OccupationAssigner.IMGS['background'].get_size())
		self.genSurf()
		self.tooltip = Tooltip('BLANK TOOLTIP', (self.rect.left + GAP, self.rect.bottom + GAP))
		self.displayTooltip = False
		self.lastHovered = None


	def update(self):
		my.screen.blit(self.surf, self.rect)
		self.displayTooltip = False
		self.handleInput()
		self.tooltip.simulate(self.displayTooltip)


	def genSurf(self):
		"""Generate a new surf (blit human imgs and +/- imgs to the background) and rects for buttons"""
		xMargin = 10
		xInterval = 28
		yMargin = 10
		yInterval = 30
		self.surf = OccupationAssigner.IMGS['background'].copy()

		self.humanRectsLocal = []
		self.humanRectsGlobal = []
		self.plusRectsLocal = []
		self.minusRectsLocal = []
		self.plusRectsGlobal = []
		self.minusRectsGlobal = []

		numOccupations = len(OccupationAssigner.OCCUPATIONIMGS)
		numColumns = math.ceil(numOccupations / OccupationAssigner.MAXCOLUMNS)
		if numColumns < 3:
			numRows = numColumns
		else:
			numRows = 3
		currentColumn = 0
		currentRow = 0

		# SET UP SURFS AND RECTS
		for i in range(len(OccupationAssigner.OCCUPATIONIMGS)):
			# HUMAN IMGS
			localHumanRect = pygame.Rect((xMargin + xInterval * currentColumn, yMargin + yInterval * currentRow), (10,20))
			self.humanRectsLocal.append(localHumanRect)
			self.surf.blit(OccupationAssigner.OCCUPATIONIMGS[i], localHumanRect)

			globalHumanRect = localHumanRect.copy()
			globalHumanRect.left += self.leftx
			globalHumanRect.top += self.topy
			self.humanRectsGlobal.append(globalHumanRect)

			# +/- IMGS
			localPlusRect = pygame.Rect(localHumanRect.topleft, OccupationAssigner.IMGS['plus'].get_size())
			localMinusRect = localPlusRect.copy()
			localPlusRect.top += 1
			localPlusRect.left += 14
			if i > 0: # no +/- for serfs
				self.surf.blit(OccupationAssigner.IMGS['plus'], localPlusRect)
			localMinusRect.top += 11
			localMinusRect.left += 14
			if i > 0: # no +/- for serfs
				self.surf.blit(OccupationAssigner.IMGS['minus'], localMinusRect)

			globalPlusRect = localPlusRect.copy()
			globalPlusRect.left += self.leftx
			globalPlusRect.top += self.topy
			self.plusRectsGlobal.append(globalPlusRect)
			globalMinusRect = localMinusRect.copy()
			globalMinusRect.top += self.topy
			globalMinusRect.left += self.leftx
			self.minusRectsGlobal.append(globalMinusRect)

			currentRow += 1
			if currentRow >= 3:
				currentColumn += 1
				currentRow = 0


	def handleInput(self):
		"""Updates the hover and click images, and changes occupation counts"""
		hovered = None
		if self.rect.collidepoint(my.input.mousePos): # avoid unnecessary collision detection
			for i in range(len(self.humanRectsGlobal)):
				if self.humanRectsGlobal[i].collidepoint(my.input.mousePos) or self.plusRectsGlobal[i].collidepoint(my.input.mousePos)\
												or self.minusRectsGlobal[i].collidepoint(my.input.mousePos):
					hovered = self.humanRectsGlobal[i]
					self.displayTooltip = True
					if mob.OCCUPATIONS[i] == 'None':
						job = 'No job'
						trueJob = None # because otherwise it checks for 'None' instead of None
					else:
						job = mob.OCCUPATIONS[i].capitalize()
						trueJob = mob.OCCUPATIONS[i]
					num = 0 # number of humans with hovered job
					for human in my.allHumans.sprites():
						if human.occupation == trueJob: num += 1
					self.tooltip.text = '%s - %s' %(job, num)
					if self.tooltip.rect.right > my.WINDOWWIDTH:
						self.tooltip.rect.right = my.WINDOWWIDTH - 1

				if self.plusRectsGlobal[i].collidepoint(my.input.mousePos):
					hovered = self.plusRectsGlobal[i]
					my.screen.blit(OccupationAssigner.IMGS['plusHover'], self.plusRectsGlobal[i])
					if my.input.mousePressed == 1:
						my.screen.blit(OccupationAssigner.IMGS['plusClick'], self.plusRectsGlobal[i])
					if my.input.mouseUnpressed == 1:
						if mob.OCCUPATIONS[i] is not 'None':
							for human in my.allHumans.sprites():
								if human.occupation == None:
									human.changeOccupation(mob.OCCUPATIONS[i])
									sound.play('click', 0.8, False)
									return
						sound.play('error', 0.4, False)

				elif self.minusRectsGlobal[i].collidepoint(my.input.mousePos):
					hovered = self.minusRectsGlobal[i]
					my.screen.blit(OccupationAssigner.IMGS['minusHover'], self.minusRectsGlobal[i])
					if my.input.mousePressed == 1:
						my.screen.blit(OccupationAssigner.IMGS['minusClick'], self.minusRectsGlobal[i])
					if my.input.mouseUnpressed == 1:
						for human in my.allHumans.sprites():
							if human.occupation == mob.OCCUPATIONS[i]:
								human.changeOccupation(None)
								sound.play('click', 0.8, False)
								return
						sound.play('error', 0.4, False)
			if hovered != self.lastHovered and hovered is not None:
				sound.play('tick', 0.8, False)
		self.lastHovered = hovered



class MissionProgressBar:
	"""Displays a progress bar showing progress through the current my.mission"""
	showTooltipTime = 10
	missionCompleteDisplayTime = 3
	def __init__(self):
		self.fgImg = pygame.image.load('assets/ui/missionBar/bar.png').convert_alpha() # foreground img
		self.progressImg = pygame.image.load('assets/ui/missionBar/progressBar.png').convert_alpha()
		self.bgImg = pygame.image.load('assets/ui/missionBar/barBg.png').convert_alpha() # background img
		self.rect = pygame.Rect((0, 0), self.fgImg.get_size())
		self.rect.midtop = (int(my.WINDOWWIDTH / 2), GAP * 4)

		self.lastProgress = -1 # always gen surf on first update
		self.lastTipShowTime = 0
		self.lastMissionEndTime = 0

		self.missionComplete = False
		self.tooltip = Tooltip('BLANK TOOLTIP', (self.rect.right + GAP, self.rect.top), BIGFONT, my.WHITE)


	def update(self):
		if my.mission:
			progress = my.mission.getProgress()
			if progress != self.lastProgress:
				self.genSurf()
			if progress >= 100 and not self.missionComplete:
				sound.play('achievement', 0.8, 0)
				self.ticksTillNextMission = 100
				self.missionComplete = True
				self.tooltip.text = 'MISSION COMPLETE:   ' + my.mission.name
				my.mission.onComplete()
			if not self.missionComplete:
				self.tooltip.text = my.mission.name.upper() + ' :  ' + my.mission.description
				self.lastMissionEndTime = time.time()

			self.tooltip.simulate(self.shouldShowTooltip())
			my.screen.blit(self.surf, self.rect)

			if self.lastMissionEndTime and time.time() - self.lastMissionEndTime > MissionProgressBar.missionCompleteDisplayTime:
				firstTime = True
				while my.mission.getProgress() == 100: # skip missions until an uncompleted one is found
					my.currentMissionNum += 1
					try:
						my.mission = my.MISSIONS[my.currentMissionNum]
					except IndexError:
						if not my.DEBUGMODE and my.mission is not None:
							ui.StatusText('Congratulations, you completed all missions!')
						my.mission = None
					if not firstTime:
						my.mission.onComplete()
						firstTime = False

				self.missionComplete = False
				self.lastTipShowTime = time.time()
				self.lastMissionEndTime = 0
			self.lastProgress = progress


	def genSurf(self):
		self.surf = self.bgImg.copy()
		self.surf.blit(self.progressImg, (2,2), pygame.Rect(2, 2, int(my.mission.getProgress() / 100 * 117) , 20))
		self.surf.blit(self.fgImg, (0,0))


	def shouldShowTooltip(self):
		"""A little function that decides if the tooltip should be shown"""
		return (self.rect.collidepoint(my.input.mousePos) or\
				time.time() - self.lastTipShowTime < MissionProgressBar.showTooltipTime or\
				time.time() - self.lastMissionEndTime < MissionProgressBar.missionCompleteDisplayTime)



class SelectionButtons:
	"""Is visible when units are selected, shows unit count and clicking the X deselects the units"""
	circleImg = pygame.image.load('assets/ui/selection buttons/circle.png').convert_alpha()
	dismissImg = pygame.image.load('assets/ui/cross.png').convert_alpha()
	dismissHoverImg = pygame.image.load('assets/ui/crossHover.png').convert_alpha()
	def __init__(self, minimap):
		self.rect = pygame.Rect((0, 0), (SelectionButtons.circleImg.get_width() * 2 + GAP * 8,
										 SelectionButtons.circleImg.get_height() + GAP * 4))
		self.rect.bottomright = (minimap.rect.left - GAP * 8, minimap.rect.bottom)
		self.alpha = 0
		self.genSurf()

		self.crossWasHovered = False

		self.lastNumSwordsmen, self.lastNumArchers = -1, -1


	def genSurf(self):
		self.baseSurf = pygame.Surface(self.rect.size)
		self.baseSurf.set_colorkey(my.COLOURKEY)
		self.baseSurf.fill(my.COLOURKEY)
		titleSurf, titleRect = genText('Selected troops', (0, 0), my.WHITE)
		self.baseSurf.blit(titleSurf, titleRect)

		self.dismissRect = SelectionButtons.dismissImg.get_rect()
		self.dismissRect.midright = (self.rect.width - 5, self.rect.height / 2)
		self.baseSurf.blit(SelectionButtons.dismissImg, self.dismissRect)

		self.dismissRectGlobal = self.dismissRect.copy()
		self.dismissRectGlobal.x += self.rect.x
		self.dismissRectGlobal.y += self.rect.y

		self.swordsmenRect = SelectionButtons.circleImg.get_rect()
		self.swordsmenRect.bottomleft = (0, self.rect.height)
		self.archersRect = self.swordsmenRect.copy()
		self.archersRect.left = self.swordsmenRect.right + GAP
		for circleRect in self.swordsmenRect, self.archersRect:
			self.baseSurf.blit(SelectionButtons.circleImg, circleRect)

		unscaledSword = pygame.image.load('assets/items/sword.png').convert_alpha()
		scaledSword = pygame.transform.scale2x(unscaledSword)
		swordRect = scaledSword.get_rect()
		swordRect.center = self.swordsmenRect.center
		self.baseSurf.blit(scaledSword, swordRect)


	def update(self, dt):
		self.surf = self.baseSurf.copy()
		if my.selectedTroops:

			if self.alpha < 255:
				self.alpha += 1350 * dt
				self.surf.set_alpha(self.alpha)

			numSwordsmen, numArchers = 0, 0
			for soldier in my.selectedTroops:
				if soldier.occupation == 'swordsman':
					numSwordsmen += 1
				elif soldier.occupation == 'archer':
					numArchers += 1

			# UPDATE NUMBER SURFS
			if numSwordsmen != self.lastNumSwordsmen:
				self.numSwordsmenSurf, self.numSwordsmenRect = genText(str(numSwordsmen), (0, 0), my.WHITE, BIGFONT)
				self.numSwordsmenRect.center = self.swordsmenRect.center
			self.surf.blit(self.numSwordsmenSurf, self.numSwordsmenRect)
			if numArchers != self.lastNumArchers:
				self.numArchersSurf, self.numArchersRect = genText(str(numArchers), (0, 0), my.WHITE, BIGFONT)
				self.numArchersRect.center = self.archersRect.center
			self.surf.blit(self.numArchersSurf, self.numArchersRect)
			self.lastNumSwordsmen, self.lastNumArchers = numSwordsmen, numArchers

			# DISMISS BUTTON
			if self.dismissRectGlobal.collidepoint(my.input.mousePos):
				self.surf.blit(SelectionButtons.dismissHoverImg, self.dismissRect)
				if not self.crossWasHovered:
					sound.play('tick', 0.8, 1)
				self.crossWasHovered = True

				if my.input.mouseUnpressed == 1:
					my.selectedTroops = pygame.sprite.Group()
					sound.play('click', 0.8, 1)

			my.screen.blit(self.surf, self.rect)

			# ISSUE MOVE COMMANDS
			# if right click is pressed order selected troops to a square around the clicked coord
			if my.input.mouseUnpressed == 3 and my.input.hoveredCell is not None:
				sound.play('click', 0.7, 1)
				MoveMarker(my.input.hoveredCell)
				if len(my.selectedTroops) == 1:
					my.selectedTroops.sprites()[0].destination = my.input.hoveredCell
				else:
					for soldier in my.selectedTroops:
						soldier.destination = 'unspecified'

					squareWidth = math.ceil(math.sqrt(len(my.selectedTroops)))
					halfSquareWidth = int(math.ceil(squareWidth / 2))
					for y in range(my.input.hoveredCell[1] - halfSquareWidth, my.input.hoveredCell[1] + halfSquareWidth):
						for x in range(my.input.hoveredCell[0] - halfSquareWidth, my.input.hoveredCell[0] + halfSquareWidth):
							for soldier in my.selectedTroops:
								if soldier.destination == 'unspecified':
									if my.map.inBounds((x, y + 1)):
										soldier.destination = (x, y + 1)
										break
									else:
										soldier.destination = my.input.hoveredCell

		else:
			self.crossWasHovered = False
			if self.alpha > 0:
				self.alpha -= 2500 * dt
				self.surf.set_alpha(self.alpha)
				my.screen.blit(self.surf, self.rect)



class UItip(pygame.sprite.Sprite):
	"""A tooltip that appears beside a UI element when the player forgets to click on something"""
	dismissImg = pygame.image.load('assets/ui/cross.png').convert_alpha()
	dismissImg = pygame.transform.scale(dismissImg, (10, 10))
	currentTips = []

	def __init__(self, toprightPos, text):
		my.ongoingUItipTexts.append(text)
		if text in UItip.currentTips: # UItip is already active or has been manually dismissed
			return


		pygame.sprite.Sprite.__init__(self)
		my.UItips.add(self)
		self.text = text
		UItip.currentTips.append(text)

		self.tooltip = Tooltip(text, (0, 0), BASICFONT, my.WHITE, 'right')
		self.tooltip.rect.topright = toprightPos
		self.tooltip.lockAlpha = True
		self.tooltip.alpha = 200

		self.dismissButtonRect = pygame.Rect((self.tooltip.rect.right - GAP*3, self.tooltip.rect.top + GAP),
											  UItip.dismissImg.get_size())
		w, h = self.tooltip.surf.get_size()


	def update(self, autoDismiss):
		if autoDismiss:
			if autoDismiss and self.text in UItip.currentTips: UItip.currentTips.remove(self.text)
			self.tooltip.lockAlpha = False

		self.tooltip.simulate(False, 0)



class BuildingMenu(pygame.sprite.Sprite):
	"""A menu that appears when the building is hovered. Allows orders to be given."""
	IMGS = {}
	for name in ['plus', 'plusHover', 'plusClick', 'minus', 'minusHover', 'minusClick']:
		IMGS[name] = pygame.image.load('assets/ui/occupationAssigner/%s.png' %(name)).convert_alpha()
	def __init__(self, building, orderList, tooltipList):
		assert len(orderList) == len(tooltipList), '%s\'s building menu has invalid arguments' %(building.name)
		pygame.sprite.Sprite.__init__(self)
		self.add(my.buildingMenus)
		self.building, self.orderList = building, orderList
		self.topright = (self.building.rect.left - GAP, self.building.tooltip.rect.top)
		self.alpha = 250
		self.lastHovered = None
		self.genSurf()
		self.genTooltips(tooltipList)


	def update(self):
		self.handleInput()
		self.updateOrderNumbers()
		for i in range(len(self.tooltips)):
			hovered = i == self.hoveredTooltip
			self.tooltips[i].simulate(hovered, True)


	def genSurf(self):
		"""Generate baseSurf and a bajillion rects"""
		iconSize = 20 # width=height
		self.iconSize = iconSize # lazy programming   D:
		plusMinusSize = 8 # width=height
		self.imgList = []
		self.topleft  = (self.building.rect.left - GAP - iconSize - plusMinusSize * 2 - GAP * 4, self.building.tooltip.rect.top)
		# RETRIEVE AND SCALE IMAGES TO iconSize
		self.rawImgList = []
		for order in self.orderList:
			self.rawImgList.append(order.image)
		for i in range(len(self.rawImgList)):
			img = pygame.transform.scale(self.rawImgList[i], (iconSize, iconSize))
			self.imgList.append(img)

		# INIT SURF
		tempSurf = pygame.Surface((iconSize + plusMinusSize * 2 + GAP * 4, 1000))
		tempSurf.fill(my.GREYBROWN)

		# GEN RECTS AND SURF
		self.iconRectsLocal = []
		self.iconRectsGlobal = []
		self.plusRectsLocal = []
		self.plusRectsGlobal = []
		self.minusRectsLocal = []
		self.minusRectsGlobal = []

		for i in range(len(self.imgList)):
			# ICONS
			iconRect = pygame.Rect((GAP, iconSize * i + GAP * (i + 1)), (iconSize, iconSize))
			self.iconRectsLocal.append(iconRect)
			tempSurf.blit(self.imgList[i], iconRect)

			globalIconRect = iconRect.copy()
			globalIconRect.move_ip(self.topleft)
			self.iconRectsGlobal.append(globalIconRect)

			# PLUS
			plusRect = pygame.Rect((0, 0), BuildingMenu.IMGS['plus'].get_size())
			plusRect.midleft = (iconRect.right + GAP, iconRect.centery)
			self.plusRectsLocal.append(plusRect)
			tempSurf.blit(BuildingMenu.IMGS['plus'], plusRect)

			globalPlusRect = plusRect.copy()
			globalPlusRect.move_ip(self.topleft)
			self.plusRectsGlobal.append(globalPlusRect)

			# MINUS
			minusRect = plusRect.copy()
			minusRect.left = plusRect.right + GAP
			self.minusRectsLocal.append(minusRect)
			tempSurf.blit(BuildingMenu.IMGS['minus'], minusRect)

			globalMinusRect = minusRect.copy()
			globalMinusRect.move_ip(self.topleft)
			self.minusRectsGlobal.append(globalMinusRect)

			if i == len(self.imgList) - 1: # bottom item
				surfHeight = iconRect.bottom + GAP
				self.baseSurf = pygame.Surface((tempSurf.get_width(), surfHeight))
				self.baseSurf.blit(tempSurf, (0,0))

		self.rect = self.baseSurf.get_rect()
		self.rect.topright = self.topright
		self.displayRect = self.rect.copy()
		self.displayRect.inflate(10, 0)

		# TRIANGLE SURF
		self.triangleSurf = pygame.Surface((10, 10))
		pygame.draw.polygon(self.triangleSurf, my.GREYBROWN, [(0, 0), (GAP, 5), (0, 10)])
		self.triangleSurf.set_colorkey(my.BLACK)


	def genTooltips(self, textList):
		"""Generates the list self.tooltips from tooltipList, which correspond to each icon (hopefully)"""
		self.tooltips = []
		for i in range(len(textList)):
			tooltipText = textList[i] + '  | ' + str(self.orderList[i].prerequisites)
			self.tooltips.append(Tooltip(tooltipText, (self.rect.right + GAP, self.rect.top + i*self.iconSize + i*GAP)))
		self.hoveredTooltip = None


	def handleInput(self):
		if self.alpha > 0: self.alpha -= 20
		if (self.displayRect.collidepoint(my.input.hoveredPixel) and self.alpha > 50) or self.building.rect.collidepoint(my.input.hoveredPixel):
			self.alpha += 60
			if self.alpha > 230:
				self.alpha = 230
			my.UIhover = True

		if self.alpha > 0 and my.camera.isVisible(self.rect):
			self.baseSurf.set_alpha(self.alpha)
			my.surf.blit(self.baseSurf, self.rect)
			self.triangleSurf.set_alpha(self.alpha)
			my.surf.blit(self.triangleSurf, (self.rect.right, self.rect.top + GAP))
			hovered = None
			self.hoveredTooltip = None
			for i in range(len(self.iconRectsGlobal)):
				if self.iconRectsGlobal[i].collidepoint(my.input.hoveredPixel):
					self.hoveredTooltip = i

				if self.plusRectsGlobal[i].collidepoint(my.input.hoveredPixel):
					my.surf.blit(BuildingMenu.IMGS['plusHover'], self.plusRectsGlobal[i])
					hovered = self.plusRectsGlobal[i]
					self.hoveredTooltip = i
					if my.input.mousePressed == 1:
						my.surf.blit(BuildingMenu.IMGS['plusClick'], self.plusRectsGlobal[i])
					if my.input.mouseUnpressed == 1:
						sound.play('click')
						self.building.orders.append(self.orderList[i])
					break

				if self.minusRectsGlobal[i].collidepoint(my.input.hoveredPixel):
					my.surf.blit(BuildingMenu.IMGS['minusHover'], self.minusRectsGlobal[i])
					hovered = self.minusRectsGlobal[i]
					self.hoveredTooltip = i
					if my.input.mousePressed == 1:
						my.surf.blit(BuildingMenu.IMGS['minusClick'], self.minusRectsGlobal[i])
					if my.input.mouseUnpressed == 1:
						try:
							self.building.orders.remove(self.orderList[i])
						except ValueError:
							sound.play('error')
						else:
							sound.play('click')
					break
			if hovered != self.lastHovered and hovered:
				sound.play('tick')
			self.lastHovered = hovered


	def updateOrderNumbers(self):
		for i in range(len(self.orderList)):
			if self.building.orders.count(self.orderList[i]) > 0 and self.alpha > 50:
				surf, rect = genText(str(self.building.orders.count(self.orderList[i])), (0,0), my.WHITE)
				rect.center = self.iconRectsGlobal[i].center
				my.surf.blit(surf, rect)



class Highlight:
	"""Highlight the cell the mouse is hovering over"""
	animateInterval = 0.15

	IMGS = {}
	colours = ['red', 'yellow', 'blue']
	for colour in colours:
		IMGS[colour] = []
		for i in range(1, len(colours) + 1):
			IMGS[colour].append(pygame.image.load('assets/ui/highlights/highlight ' + colour + str(i) + '.png').convert_alpha())

	def __init__(self, colour):
		"""Execute once for each colour, then just update its cell when need be"""
		self.animNum = 0
		self.lastAnimTime = 0

		self.numChange = 1
		self.imgs = Highlight.IMGS[colour]
		self.numImgs = len(self.imgs) - 1
		self.frames = 0


	def update(self, cell):
		cellx, celly = cell
		x, y = cellx * my.CELLSIZE, celly * my.CELLSIZE
		my.surf.blit(self.imgs[self.animNum], (x, y))

		if time.time() - self.lastAnimTime > Highlight.animateInterval:
			if self.animNum == self.numImgs: self.numChange = -1
			elif self.animNum == 0: self.numChange = 1
			self.animNum += self.numChange
			self.lastAnimTime = time.time()



class SelectionBox(pygame.sprite.Sprite):
	"""A click and drag selected area, detects the presence of tiles within"""
	def __init__(self, designateTrees, designateOres, designateSoldiers):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.selectionBoxGroup)
		self.designateTrees, self.designateOres, self.designateSoldiers = designateTrees, designateOres, designateSoldiers
		if self.designateTrees:
			self.colour = my.GREEN
		elif self.designateOres:
			self.colour = my.DARKGREY
		elif self.designateSoldiers:
			self.colour = my.RED
			if pygame.locals.K_LSHIFT not in my.input.pressedKeys: # if shift is pressed add to current selection
				my.selectedTroops = pygame.sprite.Group()         # else replace current selection
		else:
			self.colour = my.BLUE
		if my.input.hoveredCell:
			self.origin = my.input.hoveredCell
		else:
			self.kill()
			return
		self.end = self.origin
		my.mode = 'build'


	def update(self):
		if my.input.mouseUnpressed and my.input.hoveredCell:
			self.end = my.input.hoveredCell
			self.finishSelection()
		elif my.input.hoveredCell:
			self.end = my.input.hoveredCell
			ox, oy = my.map.cellsToPixels(self.origin)
			ex, ey = my.map.cellsToPixels(self.end)
			if ox > ex:
				leftx = ex
				rightx = ox
			else:
				leftx = ox
				rightx = ex
			if oy > ey:
				topy = ey
				bottomy = oy
			else:
				topy = oy
				bottomy = ey
			rect = pygame.Rect((leftx, topy), (rightx - leftx, bottomy - topy))
			surf = pygame.Surface(rect.size)
			surf.fill(self.colour)
			surf.set_alpha(100)
			my.surf.blit(surf, rect)


	def finishSelection(self):
		"""Calculates the selected stuff, called when mouse is released"""
		my.mode = 'look'
		selected = pygame.sprite.Group()

		if not self.designateSoldiers:
			if self.designateTrees:
				group = my.designatedTrees
				maxDesignated = my.MAXTREESDESIGNATED
				terrainTypes = ['tree']

			elif self.designateOres:
				group = my.designatedOres
				maxDesignated = my.MAXORESDESIGNATED
				terrainTypes = ['coal', 'iron', 'gold']

			for terrainType in terrainTypes:
				selected.add((self.findTerrainType(terrainType, group)).sprites())

		if self.designateSoldiers:
			ox, oy = self.origin
			ex, ey = self.end
			startx = min(ox, ex)
			endx = max(ox, ex)
			starty = min(oy, ey)
			endy = max(oy, ey)
			for x in range(startx, endx):
				for y in range(starty, endy):
					for human in my.allHumans:
						if human.occupation in ['swordsman', 'archer'] and human.coords == (x, y):
							my.selectedTroops.add(human)
							PulseLight((0, 0), my.ORANGE, human)
			if my.selectedTroops:
				sound.play('swish', 0.4, 1)

		alerted = False
		if selected and not self.designateSoldiers:
			for sprite in selected.sprites():
				if len(group) < maxDesignated:
					group.add(sprite)
				else:
					if not alerted: 
						StatusText('Woah, too many %s designated! Your workers have forgotten some.' %(terrainTypes))
						alerted = True
			sound.play('swish', 0.4, 1)
		my.designationMode = None
		self.kill()


	def findTerrainType(self, terrainType, currentGroup):
		"""Returns a list of tuple coords of all trees in the SelectionBox"""
		self.selected = pygame.sprite.Group()
		ox, oy = self.origin
		ex, ey = self.end
		startx = min(ox, ex)
		endx = max(ox, ex)
		starty = min(oy, ey)
		endy = max(oy, ey)
		for x in range(startx, endx):
			for y in range(starty, endy):
				if my.map.map[x][y] == terrainType and (x, y):
					coordsInGroup = False
					for sprite in currentGroup.sprites():
						if (x, y) == sprite.coords:
							coordsInGroup = True
					if not coordsInGroup:
						self.selected.add(my.map.getObj((x, y), terrainType))
						if self.designateTrees: PulseLight((x, y), my.GREEN)
						elif self.designateOres: PulseLight((x, y), my.LIGHTGREY)
		return self.selected



class Demolisher(pygame.sprite.Sprite):
	"""Demolishes the hovered building when LMB is clicked"""
	bombImg = pygame.image.load('assets/ui/bomb.png').convert_alpha()
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.demolisher)


	def update(self):
		my.mode = 'build'
		hoveredSite = self.getHoveredSite()
		if hoveredSite:
			my.surf.blit(hoveredSite.scaledCross, hoveredSite.rect)
			if my.input.mouseUnpressed == 1:
				hoveredSite.demolish()
				sound.play('explosion')
				self.kill()
				my.mode = 'look'
		else:
			my.surf.blit(Demolisher.bombImg, my.map.cellsToPixels(my.input.hoveredCell))


	def getHoveredSite(self):
		"""Returns the hovered building, if one is hovered"""
		if my.input.mousePressed == 3:
			self.kill()
			my.mode = 'look'
		return building.findBuildingAtCoord(my.input.hoveredCell)



class PulseLight(pygame.sprite.Sprite):
	"""A coloured circle that appears on a coord then disappears"""
	lifetime = 600
	def __init__(self, coords, colour, follow=None):
		pygame.sprite.Sprite.__init__(self)
		my.pulseLights.add(self)

		if follow:
			self.follow = follow
			x, y = my.map.cellsToPixels(self.follow.coords)
		else:
			x, y = my.map.cellsToPixels(coords)
			self.follow = None

		self.pos = (x + my.HALFCELL, y + my.HALFCELL)
		self.colour = colour
		self.startTime = time.time()


	def update(self):
		if time.time() - self.startTime > PulseLight.lifetime and not self.follow:
			self.kill()
		else:
			if self.follow:
				self.pos = self.follow.rect.center
				if self.follow not in my.selectedTroops: self.kill()

			pygame.draw.circle(my.surf, self.colour, self.pos, my.HALFCELL, 2)



class MoveMarker(pygame.sprite.Sprite):
	"""An animated arrow to indicate where move commands have been issued to"""
	imgs = []
	for i in range(1, 15):
		imgs.append(pygame.image.load('assets/ui/commandMarker/%s.png' %(i)).convert_alpha())
	def __init__(self, coords):
		pygame.sprite.Sprite.__init__(self)
		my.moveMarkers.add(self)
		self.animNum = 0
		self.coords = coords


	def update(self):
		if my.ticks % 3 == 0:
			self.animNum += 1
		if self.animNum >= 14:
			self.kill()
		else:
			my.surf.blit(MoveMarker.imgs[self.animNum], my.map.cellsToPixels(self.coords))



class StatusArea:
	"""Handles any status messages that occur, moving them down and fading them out"""
	def __init__(self):
		my.statuses = pygame.sprite.Group()
		my.recentStatuses = pygame.sprite.Group()
		self.statusList = []


	def update(self):
		for statusObj in my.statuses.sprites():
			if statusObj not in self.statusList:
				self.statusList = [statusObj] + self.statusList
		currentHeight = 0
		for status in self.statusList[:]:
			if status not in my.statuses: # is faded out
				self.statusList.remove(status)
			else:
				status.update(GAP * 10 + currentHeight)
				currentHeight += status.tooltip.rect.height + GAP
		for recentStatus in my.recentStatuses.sprites():
			if my.ticks - recentStatus.startTicks > StatusText.recentStatusLifetime:
				recentStatus.kill()



class StatusText(pygame.sprite.Sprite):
	"""
	Displays important info to the player.
	Is moved down when another message comes in, is faded out after a period of time
	"""
	statusLifetime = 200
	recentStatusLifetime = 1000  # how long before a status pops up again when called repeatedly
	eyeImg = pygame.image.load('assets/ui/eye.png').convert_alpha()
	def __init__(self, text, zoomTo=None, allowRepeats=False):
		if not allowRepeats:
			for obj in my.recentStatuses.sprites():
				if obj.text == text: return # don't have duplicate messages at once
		pygame.sprite.Sprite.__init__(self)
		self.add(my.statuses)
		self.add(my.recentStatuses)
		self.startTicks = my.ticks
		self.text, self.zoomTo = text, zoomTo
		self.lifetime = StatusText.statusLifetime

		self.tooltip = Tooltip(text, (10, 40), BIGFONT)
		self.tooltip.fadeRate = 1
		self.tooltip.rect.topleft = (GAP, 0)
		self.tooltip.alpha = 100
		if self.zoomTo:
			w, h = StatusText.eyeImg.get_size()
			self.tooltip.surf.blit(StatusText.eyeImg, (self.tooltip.rect.right - w - GAP, self.tooltip.rect.bottom - h - GAP))
			self.lifetime += 50
		self.fadeOut = False
		self.destination = (GAP, GAP)
		sound.play('pop', 0.8, False)


	def update(self, destinationY): # destinationY may be the StatusText's current y value
		if my.ticks - self.startTicks > self.lifetime:
			self.fadeOut = True
		self.destination = (GAP, destinationY)
		destx, desty = self.destination
		if desty > self.tooltip.rect.top:
			self.tooltip.rect.y += 5
		if self.tooltip.alpha > 0:
			self.tooltip.simulate(not self.fadeOut)
		hovered = self.tooltip.rect.collidepoint(my.input.mousePos)
		if hovered:
			self.tooltip.alpha += 20
			if self.tooltip.alpha > 200: self.tooltip.alpha = 200
		isClicked = (hovered and my.input.mouseUnpressed == 1)
		if self.tooltip.alpha < 1 or isClicked:
			self.remove(my.statuses)
			if isClicked:
				if self.zoomTo: my.camera.targetFocus = self.zoomTo
				sound.play('pop')



class Minimap:
	rawBorderImg = pygame.image.load('assets/ui/minimapBorder.png').convert_alpha()
	borderImg = pygame.transform.scale(rawBorderImg, (my.MAPXCELLS + int(my.MAPXCELLS / 10), my.MAPYCELLS + int(my.MAPYCELLS / 10)))
	"""A minimap displaying the world and the camera's viewarea, at the bottom right of the screen"""
	def __init__(self):
		self.rect = pygame.Rect((my.WINDOWWIDTH - my.MAPXCELLS - GAP * 6, my.WINDOWHEIGHT - my.MAPYCELLS - GAP * 6), (my.MAPXCELLS, my.MAPYCELLS))
		self.surf = pygame.Surface(self.rect.size)
		self.mapSurf = pygame.Surface(self.rect.size)
		self.mapSurf.fill(my.DARKGREEN)
		self.blipSurf = pygame.Surface(self.rect.size)
		self.blipSurf.set_colorkey(my.COLOURKEY)
		self.newSurf = pygame.Surface(self.rect.size)
		self.newSurf.fill(my.DARKGREEN)
		self.row = 0
		self.updateMapsurf()
		self.updateMobBlips()
		self.hoverSurf = pygame.Surface(self.rect.size)
		self.hoverSurf.fill(my.WHITE)
		self.hoverSurf.set_alpha(30)


	def update(self):
		for i in range(my.MINIMAPUPDATESPEED):
			self.updateRowOfSurf()
		self.surf.blit(self.mapSurf, (0,0))
		if my.ticks % 10 == 0:
			self.updateMobBlips()
		if my.ticks % 4 == 0 or (my.ticks + 1) % 6 == 0 or (my.ticks + 2) % 6 == 0:
			self.surf.blit(self.blipSurf, (0,0))
		else:
			self.surf = self.mapSurf.copy()
		self.updateCameraRect()
		my.screen.blit(self.surf, self.rect)
		my.screen.blit(Minimap.borderImg, (self.rect.left - int(my.MAPXCELLS / 20), self.rect.top - int(my.MAPYCELLS / 20)))
		self.handleInput()


	def updateMapsurf(self):
		"""Instantly regenerate the minimap"""
		for i in range(my.MAPYCELLS):
			self.updateRowOfSurf()


	def updateRowOfSurf(self):
		"""
		Spread out the updating so there aren't massive FPS drops.
		When updating is complete, make the newSurf the mapSurf.
		"""
		for y in range(my.MAPYCELLS):
			tile = my.map.map[self.row][y]
			if tile == 'grass': continue # background is already green
			colour = None
			if tile == 'rock': colour = my.DARKGREY
			elif tile == 'tree': colour = my.GREEN
			elif tile in ['coal', 'iron', 'gold']: colour = my.BLACK
			elif tile == 'water': colour = my.BLUE
			else:
				colour = my.YELLOW
			self.newSurf.fill(colour, (self.row, y, 1, 1))
		self.row += 1
		if self.row > my.MAPXCELLS - 1:
			self.row = 0
			self.mapSurf = self.newSurf.copy()
			self.newSurf.fill(my.DARKGREEN)


	def updateMobBlips(self):
		"""Blits dots to self.surf where certain mobs are"""
		self.blipSurf.fill(my.COLOURKEY)
		dotSurf = pygame.Surface((1, 1))
		dotSurf.fill(my.BRIGHTRED)
		for human in my.allHumans:
			self.blipSurf.blit(dotSurf, human.coords)


	def updateCameraRect(self):
		"""Update a rect showing the camera's viewArea on the map"""
		viewArea = my.camera.viewArea
		lineCoords = []
		for coord in [viewArea.topleft, viewArea.topright, viewArea.bottomright, viewArea.bottomleft]:
			lineCoords.append(my.map.pixelsToCell(coord))
		pygame.draw.lines(self.surf, my.RED, True, lineCoords, 2)


	def handleInput(self):
		"""Jump the camera to the clicked location"""
		if self.rect.collidepoint(my.input.mousePos):
			my.screen.blit(self.hoverSurf, self.rect)
			if my.input.mousePressed == 1 and not len(my.buildingBeingPlaced):
				x, y = my.input.mousePos
				x2, y2 = self.rect.topleft
				x -= x2
				y -= y2
				my.camera.focus = my.map.cellsToPixels((x, y))
