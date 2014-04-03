import pygame, my, math, building

my.selectionBoxGroup = pygame.sprite.GroupSingle()
my.pulseLights = pygame.sprite.Group()

BASICFONT = pygame.font.Font('freesansbold.ttf', 12)
PRETTYFONT = pygame.font.Font('assets/fonts/fontTitle.ttf', 12)
BIGFONT   = pygame.font.Font('assets/fonts/fontTitle.ttf', 25)
MEGAFONT  = pygame.font.Font('assets/fonts/fontTitle.ttf', 42)
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




class Hud:
	"""Handles resource amounts, buttons and tooltips"""
	def __init__(self):
		self.buttons = []
		self.tooltips = []
		self.HIGHLIGHTS = {}
		for colour in Highlight.IMGS.keys():
			self.HIGHLIGHTS[colour] = Highlight(colour)
		self.bottomBar = BottomBar()
		self.statusText = StatusText()
		my.surf = pygame.Surface(my.map.surf.get_size())
		self.regenSurf = False


	def updateHUD(self):
		"""Updates elements that are blitted to screen"""
		self.bottomBar.update()
		self.statusText.update()
		# RESOURCE AMOUNTS
		i = 0
		currentWidth = 0
		for key in my.resources.keys():
			currentWidth += resourceText('%s: %s/%s' % (key, my.resources[key], my.maxResources[key]), 
																  (GAP * (i + 1) + currentWidth, GAP))
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
		#if my.input.mousePressed == 3 and not my.selectionBoxGroup.sprite:
		#	SelectionBox('trees', False)
		if my.input.mousePressed == 3 and not my.selectionBoxGroup.sprite:
			SelectionBox(False, 'ores')
		if my.selectionBoxGroup.sprite:
			my.selectionBoxGroup.sprite.update()
		my.pulseLights.update()



	def genSurf(self):
		"""Regenerates my.surf next frame to prevent blank frames"""
		self.regenSurf = True


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
		if isHovered:
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
		self.bounds = pygame.Rect((0, my.WINDOWHEIGHT - BottomBar.height), (my.WINDOWWIDTH, BottomBar.height))
		self.tab = 0
		self.backgroundImg = pygame.image.load('assets/ui/bottomBar/background.png').convert_alpha()
		self.cellHighlight = pygame.image.load('assets/ui/bottomBar/cellHighlight.png').convert_alpha()
		self.cellClick     = pygame.image.load('assets/ui/bottomBar/cellClick.png').convert_alpha()
		self.clickedCell, self.hovered, self.lastClicked, self.lastHovered = None, None, None, None
		self.surf = pygame.Surface(self.bounds.size)
		self.surf.blit(self.backgroundImg, (0, 0))
		self.surf.set_colorkey(my.BLACK)
		self.genRects()
		self.genTooltips()
		stats = my.BUILDINGSTATS # synctactic sugar
		self.SURFS = [self.genSurf([stats['hut']['img'], stats['shed']['img'],
					  stats['orchard']['img'], stats['fishing boat']['img'], stats['fish mongers']['img'],
					  stats['town hall']['img']])]
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


	def genSurf(self, imgs):
		"""Generate a new surface with the imgs passed blitted onto it. These can be reused"""
		surf = self.backgroundImg.copy()
		assert len(imgs) <= 12, "Too many images for bottom bar!"
		for i in range(len(imgs)):
			# scale and blit preview image to BottomBar cell
			width, height = imgs[i].get_rect().size
			if width > height:
				widthScale = 50
				heightScale = int(height / width * 50)
			else:
				heightScale = 50
				widthScale = int(width / height * 50)
			img = pygame.transform.scale(imgs[i], (widthScale, heightScale))
			imgRect = img.get_rect()
			imgRect.center = self.localRects[i].center
			surf.blit(img, imgRect)
		return surf


	def genTooltips(self):
		self.tooltips = []
		for i in range(len(my.BUILDINGSTATS)):
			building = my.BUILDINGSTATS[my.BUILDINGNAMES[i]]
			text = '%s Build time: %s, Build materials needed: %s' \
					%(building['description'], building['buildTime'], building['buildMaterials'])
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
				building.TownHall()
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
		self.lastClicked, self.lastHovered = self.clickedCell, self.hovered



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
			pygame.draw.rect(my.surf, my.BLUE, rect)


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
		for terrainType in terrainTypes:
			selected.add((self.findTerrainType(terrainType, group)).sprites())
		if selected:
			for sprite in selected.sprites():
				if len(group) < maxDesignated:
					group.add(sprite)
				else:
					my.statusMessage = 'Woah, too many %s designated! Your workers have forgotten some.' %(terrainTypes)
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



class StatusText:
	"""Displays my.statusMessage as a tooltip when it is changed in the upper left of the screen"""
	def __init__(self):
		self.lastStatus = my.statusMessage
		self.pos = int(my.WINDOWWIDTH / 4) * 3, int(my.WINDOWHEIGHT / 4)
		self.tooltip = Tooltip(my.statusMessage, (10, 40), BIGFONT)
		self.tooltip.fadeRate = 1
		self.tooltip.rect.topright = self.pos
	

	def update(self):
		if my.statusMessage != self.lastStatus:
			self.tooltip.text = my.statusMessage
			self.tooltip.simulate(True)
			self.tooltip.alpha = 255
		else:
			self.tooltip.simulate(False)
		self.lastStatus = my.statusMessage

