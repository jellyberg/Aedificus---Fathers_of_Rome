import pygame, my, math, random, building, mob, sound

my.selectionBoxGroup = pygame.sprite.GroupSingle()
my.pulseLights = pygame.sprite.Group()

BASICFONT = pygame.font.Font('assets/fonts/olympus bold.ttf', 14)
PRETTYFONT = pygame.font.Font('assets/fonts/fontTitle.ttf', 12)
BIGFONT   = pygame.font.Font('assets/fonts/olympus thin.ttf', 25)
MEGAFONT  = pygame.font.Font('assets/fonts/olympus thin.ttf', 42)
GAP = 5
TOOLTIPWORDSPERLINE = 6  # subtract 1!


def genText(text, topLeftPos, colour, font):
	surf = font.render(text, 1, colour)
	rect = surf.get_rect()
	rect.topleft = topLeftPos
	return (surf, rect)


def resourceText(text, topLeftPos):
	"""Generates and blits resource amount indicators"""
	x, y = topLeftPos
	textSurf, textRect = genText(text, (GAP, GAP), my.WHITE, BASICFONT)
	bgRect = pygame.Rect((x, y), (textRect.width + GAP * 2, textRect.height + GAP * 2))
	bgSurf = pygame.Surface((bgRect.width, bgRect.height))
	bgSurf.fill(my.BROWN)
	bgSurf.blit(textSurf, textRect)
	my.screen.blit(bgSurf, bgRect)
	return bgRect.width


def handleTooltips():
	for building in my.allBuildings:
		building.handleTooltip()
	for corpse in my.corpses:
		corpse.handleTooltip()
	for mob in my.allMobs:
		mob.handleTooltip()




class Hud:
	"""Handles resource amounts, buttons and tooltips"""
	def __init__(self):
		self.buttons = []
		self.tooltips = []
		self.HIGHLIGHTS = {}
		for colour in Highlight.IMGS.keys():
			self.HIGHLIGHTS[colour] = Highlight(colour)
		self.bottomBar = BottomBar()
		self.occupationAssigner = OccupationAssigner()
		self.designator = Designator()
		self.minimap = Minimap()
		self.statusArea = StatusArea()
		my.surf = pygame.Surface(my.map.surf.get_size())
		self.regenSurf = False


	def updateHUD(self):
		"""Updates elements that are blitted to screen"""
		self.bottomBar.update()
		self.occupationAssigner.update()
		self.designator.update()
		self.minimap.update()
		self.statusArea.update()
		# RESOURCE AMOUNTS
		i = 0
		currentWidth = 0
		for key in my.resources.keys():
			currentWidth += resourceText('%s: %s' % (key, my.resources[key]), (GAP * (i + 1) + currentWidth, GAP))
			i += 1


	def updateWorldUI(self):
		"""Updates elements that are blitted to my.surf"""
		# HIGHLIGHT
		if my.mode != 'build' and my.input.hoveredCell:
			if my.mode == 'look':
				if my.input.hoveredCellType not in ['grass', 'water', 'rock']:
					currentHighlight = self.HIGHLIGHTS['yellow']
				else:
					currentHighlight = self.HIGHLIGHTS['blue']
			currentHighlight.update(my.input.hoveredCell)
		# SELECTION BOX
		if my.input.mousePressed == 3 and not my.selectionBoxGroup.sprite and my.designationMode == 'tree':
			SelectionBox('trees', False)
		if my.input.mousePressed == 3 and not my.selectionBoxGroup.sprite and my.designationMode == 'ore':
			SelectionBox(False, 'ores')
		if my.selectionBoxGroup.sprite:
			my.selectionBoxGroup.sprite.update()
		my.pulseLights.update()



	def genSurf(self):
		"""Regenerates my.surf next frame to prevent blank frames"""
		#self.regenSurf = True
		self.genBlankSurf()


	def genBlankSurf(self):
		"""Regenerates my.surf"""
		my.surf = pygame.Surface(my.map.surf.get_size())
		my.hud.updateWorldUI()



class Button:
	"""A button, can be clickable, can have tooltip. When clicked, self.isClicked=True"""
	def __init__(self, text, style, screenPos, isClickable=0, isTitle=0, screenPosIsTopRight=0, tooltip=None):
		"""style is redundant atm, tooltip should be a string"""
		self.text, self.style, self.screenPos, self.isClickable, self.posIsTopRight = \
		(text, style, screenPos, isClickable, screenPosIsTopRight)
		if isTitle:
			self.textSurf = BIGFONT.render(self.text, 1, my.LIGHTGREY)
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
		self.hasTooltip = False
		if tooltip:
			self.hasTooltip = True
			self.tooltip = Tooltip(tooltip, (self.rect.right + GAP, self.rect.top))

	def simulate(self, userInput):
		if self.isClickable or self.hasTooltip: self.handleClicks(userInput)
		if self.hasTooltip: self.tooltip.simulate(self.isHovered)
		self.draw()

	def draw(self):
		if self.posIsTopRight:
			self.rect.topright = self.screenPos
		else:
			self.rect.topleft = self.screenPos
		my.screen.blit(self.currentSurf, self.rect)

	def handleClicks(self, userInput=None):
		self.isClicked = False
		self.isHovered = False
		if self.rect.collidepoint(my.input.mousePos):
			if userInput.mousePressed == 1:
				self.currentSurf = self.clickSurf
			else:
				self.currentSurf = self.hoverSurf
				self.isHovered = True
		else:
			self.currentSurf = self.buttonSurf
		if userInput.mouseUnpressed == True and self.rect.collidepoint(my.input.mousePos):
			self.isClicked = True
			sound.play('click', 0.8, False)



class Tooltip:
	"""A multiline text box, displayed when isHovered=True"""
	def __init__(self, text, pos, font=BASICFONT):
		self.pos, self.text, self.font = pos, text, font
		self.x, self.y = pos
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
		pygame.draw.rect(self.surf, my.CREAM, (GAP, 0, self.surf.get_width() - GAP, self.surf.get_height()))
		pygame.draw.polygon(self.surf, my.CREAM, [(0, 10), (GAP, 5), (GAP, 15)])
		for i in range(len(self.textObjs)):
			self.surf.blit(self.textObjs[i][0], self.textObjs[i][1])
		self.surf.set_colorkey(my.BLACK)
		self.rect = self.surf.get_rect()
		self.rect.topleft = self.pos
		

	def simulate(self, isHovered, blitToLand=False):
		if self.text != self.lastText:
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
		testText, testRect = genText(newText[0], (0, 0), my.BLACK, self.font)
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



class BottomBar:
	"""A multi-tab menu at the bottom of the screen which allows contruction of buildings"""
	height = 50
	margin = 14 # at left hand side
	cell   = 52 # width
	def __init__(self):
		self.bounds = pygame.Rect((0, my.WINDOWHEIGHT - BottomBar.height - GAP * 2), (BottomBar.margin + BottomBar.cell * 12, BottomBar.height))
		self.tab = 0
		self.cellBackgrounds = []
		bgImg = pygame.image.load('assets/ui/bottomBar/cellBg.png').convert_alpha()
		flippedBgImg = pygame.transform.flip(bgImg, 1, 1)
		for i in range(0, 360, 90):
			self.cellBackgrounds.append(pygame.transform.rotate(bgImg, i))
			self.cellBackgrounds.append(pygame.transform.rotate(flippedBgImg, i))
		self.cellHighlight = pygame.image.load('assets/ui/bottomBar/cellHighlight.png').convert_alpha()
		self.cellClick     = pygame.image.load('assets/ui/bottomBar/cellClick.png').convert_alpha()
		self.genRects()
		self.genBackgroundImg()
		self.clickedCell, self.hovered, self.lastClicked, self.lastHovered = None, None, None, None
		self.surf = pygame.Surface(self.bounds.size)
		self.surf.blit(self.backgroundImg, (0, 0))
		self.surf.set_colorkey(my.BLACK)
		self.genTooltips()
		stats = my.BUILDINGSTATS # synctactic sugar
		self.SURFS = [self.genSurf([stats['hut']['img'], stats['shed']['img'],
					  stats['orchard']['img'], stats['fishing boat']['img'], stats['fish mongers']['img'],
					  stats['pool']['img'], stats['town hall']['img']])]
		self.surf.blit(self.SURFS[self.tab], (0, 0))


	def genRects(self):
		"""Generates a list of twelve rects, to be used for collision detection with the mouse"""
		self.localRects = []
		self.globalRects = []
		for i in range(12):
			self.localRects.append(pygame.Rect((BottomBar.margin + i * BottomBar.cell, 0), 
								   (BottomBar.cell, BottomBar.cell)))
			self.globalRects.append(pygame.Rect((BottomBar.margin + i * BottomBar.cell, my.WINDOWHEIGHT - BottomBar.height), 
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
				heightScale = int(height / width * 40)
			else:
				heightScale = 40
				widthScale = int(width / height * 40)
			img = pygame.transform.scale(imgs[i], (widthScale, heightScale))
			imgRect = img.get_rect()
			imgRect.center = self.localRects[i].center
			surf.blit(img, imgRect)
		return surf


	def genTooltips(self):
		self.tooltips = []
		for i in range(len(my.BUILDINGSTATS)):
			building = my.BUILDINGSTATS[my.BUILDINGNAMES[i]]
			text = '%s: %s Building materials needed: %s' \
					%(my.BUILDINGNAMES[i].capitalize(), building['description'], building['buildMaterials'])
			x = self.globalRects[i].right
			x += GAP
			tooltip = Tooltip(text, (x, 0))
			tooltip.rect.bottom = my.WINDOWHEIGHT - GAP
			self.tooltips.append(tooltip)


	def update(self):
		self.handleInput()
		if self.clickedCell != None:
			if self.clickedCell == 0:
				building.Hut()
			elif self.clickedCell == 1:
				building.Shed()
			elif self.clickedCell == 2:
				building.Orchard()
			elif self.clickedCell == 3:
				building.FishingBoat()
			elif self.clickedCell == 4:
				building.FishMongers()
			elif self.clickedCell == 5:
				building.Pool()
			elif self.clickedCell == 6:
				building.TownHall()
			else:
				sound.play('error', 0.2, False)
		my.screen.blit(self.surf, self.bounds)
		i=0
		for tooltip in self.tooltips:
			if self.hovered == i: hovered = True
			else: hovered = False
			tooltip.simulate(hovered)
			i += 1


	def handleInput(self):
		"""Update surf highlights and self.hovered and self.clickedCell"""
		self.clickedCell = None
		self.hovered = None
		resetted = False
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



class Designator:
	"""A menu to select the kind of SelectionBox created when RMB is pressed. Can be collapsed when the icon is clicked"""
	def __init__(self):
		my.designationMode = None
		self.baseSurf = pygame.image.load('assets/ui/designator/background.png')
		self.surf = self.baseSurf.copy()
		self.COLLAPSEDTOPLEFT = (my.WINDOWWIDTH - 10, int(my.WINDOWHEIGHT / 5))
		self.OPENTOPLEFT      = (my.WINDOWWIDTH - self.surf.get_width(), int(my.WINDOWHEIGHT / 5))
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
		self.handleTab()
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
						my.designationMode = 'tree'
					elif i == 1:
						my.designationMode = 'ore'
					sound.play('click', 0.8, False)
			i += 1



class OccupationAssigner:
	"""A dialogue box to +/- the number of each occupation"""
	IMGS = {}
	for name in ['background', 'plus', 'plusHover', 'plusClick', 'minus', 'minusHover', 'minusClick']:
		IMGS[name] = pygame.image.load('assets/ui/occupationAssigner/%s.png' %(name)).convert_alpha()
	OCCUPATIONIMGS = [mob.Human.idleAnimation[0], mob.Human.builderIdleAnim[0], mob.Human.woodcutterIdleAnim[0],
					  mob.Human.minerIdleAnim[0], mob.Human.fishermanIdleAnim[0]]
	MAXCOLUMNS = 3
	def __init__(self):
		self.leftx = my.WINDOWWIDTH - OccupationAssigner.IMGS['background'].get_width() - GAP
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



class Highlight:
	"""Highlight the cell the mouse is hovering over"""
	IMGS = {}
	colours = ['red', 'yellow', 'blue']
	for colour in colours:
		IMGS[colour] = []
		for i in range(1, len(colours) + 1):
			IMGS[colour].append(pygame.image.load('assets/ui/highlights/highlight ' + colour + str(i) + '.png').convert_alpha())

	def __init__(self, colour):
		"""Execute once for each colour, then just update its cell when need be"""
		self.animNum = 0
		self.numChange = 1
		self.imgs = Highlight.IMGS[colour]
		self.numImgs = len(self.imgs) - 1
		self.frames = 0


	def update(self, cell):
		self.frames += 1
		cellx, celly = cell
		x, y = cellx * my.CELLSIZE, celly * my.CELLSIZE
		my.surf.blit(self.imgs[self.animNum], (x, y))
		if self.frames % 5 == 0:
			if self.animNum == self.numImgs: self.numChange = -1
			elif self.animNum == 0: self.numChange = 1
			self.animNum += self.numChange
		my.updateSurf = True



class SelectionBox(pygame.sprite.Sprite):
	"""A click and drag selected area, detects the presence of tiles within"""
	def __init__(self, designateTrees, designateOres):
		pygame.sprite.Sprite.__init__(self)
		self.add(my.selectionBoxGroup)
		self.designateTrees, self.designateOres = designateTrees, designateOres
		if self.designateTrees:
			self.colour = my.GREEN
		elif self.designateOres:
			self.colour = my.DARKGREY
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
		if self.designateTrees:
			group = my.designatedTrees
			maxDesignated = my.MAXTREESDESIGNATED
			terrainTypes = ['tree']
		elif self.designateOres:
			group = my.designatedOres
			maxDesignated = my.MAXORESDESIGNATED
			terrainTypes = ['coal', 'iron']
		selected = pygame.sprite.Group()
		alerted = False
		for terrainType in terrainTypes:
			selected.add((self.findTerrainType(terrainType, group)).sprites())
		if selected:
			for sprite in selected.sprites():
				if len(group) < maxDesignated:
					group.add(sprite)
				else:
					if not alerted: 
						StatusText('Woah, too many %s designated! Your workers have forgotten some.' %(terrainTypes))
						alerted = True
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
						PulseLight((x, y), my.ORANGE)
		return self.selected



class PulseLight(pygame.sprite.Sprite):
	"""A coloured circle that appears on a coord then disappears"""
	def __init__(self, coords, colour):
		pygame.sprite.Sprite.__init__(self)
		my.pulseLights.add(self)
		x, y = my.map.cellsToPixels(coords)
		self.pos = (x + my.HALFCELL, y + my.HALFCELL)
		self.colour = colour
		self.time = 20


	def update(self):
		if self.time < 1:
			self.kill()
		else:
			pygame.draw.circle(my.surf, self.colour, self.pos, my.HALFCELL, 2)
			self.time -=1



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
	def __init__(self, text):
		for obj in my.recentStatuses.sprites():
			if obj.text == text: return # don't have duplicate messages at once
		pygame.sprite.Sprite.__init__(self)
		self.add(my.statuses)
		self.add(my.recentStatuses)
		self.startTicks = my.ticks
		self.text = text
		self.tooltip = Tooltip(text, (10, 40), BIGFONT)
		self.tooltip.fadeRate = 1
		self.tooltip.rect.topleft = (GAP, 0)
		self.tooltip.alpha = 100
		self.fadeOut = False
		self.destination = (GAP, GAP)
		sound.play('pop', 0.8, False)


	def update(self, destinationY): # destinationY may be the StatusText's current y value
		if my.ticks - self.startTicks > StatusText.statusLifetime:
			self.fadeOut = True
		self.destination = (GAP, destinationY)
		destx, desty = self.destination
		if desty > self.tooltip.rect.top:
			self.tooltip.rect.y += 5
		if self.tooltip.alpha > 0:
			self.tooltip.simulate(not self.fadeOut)
		isClicked = (self.tooltip.rect.collidepoint(my.input.mousePos) and my.input.mouseUnpressed == 1)
		if self.tooltip.alpha < 1 or isClicked:
			self.remove(my.statuses)
			if isClicked:
				sound.play('pop')



class Minimap:
	borderImg = pygame.image.load('assets/ui/minimapBorder.png')
	"""A minimap displaying the world and the camera's viewarea, at the bottom right of the screen"""
	def __init__(self):
		self.rect = pygame.Rect((my.WINDOWWIDTH - my.MAPXCELLS - GAP * 4, my.WINDOWHEIGHT - my.MAPYCELLS - GAP * 4), (my.MAPXCELLS, my.MAPYCELLS))
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
		my.screen.blit(Minimap.borderImg, (self.rect.left - 10, self.rect.top - 10))
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
			elif tile == 'coal': colour = my.BLACK
			elif tile == 'iron': colour = my.ORANGE
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
			if my.input.mousePressed == 1:
				x, y = my.input.mousePos
				x2, y2 = self.rect.topleft
				x -= x2
				y -= y2
				my.camera.focus = my.map.cellsToPixels((x, y))
