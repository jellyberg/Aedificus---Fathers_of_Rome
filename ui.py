import pygame, my, input, math
pygame.init()

BASICFONT = pygame.font.Font('freesansbold.ttf', 12)
PRETTYFONT = pygame.font.Font('assets/fonts/fontTitle.ttf', 12)
BIGFONT   = pygame.font.Font('assets/fonts/fontTitle.ttf', 25)
MEGAFONT  = pygame.font.Font('assets/fonts/fontTitle.ttf', 42)
GAP = 5
TOOLTIPWORDSPERLINE = 6  # subtract 1!


def genText(text, topLeftPos, colour, isTitle=0, isMega=0, centerPos=0, isPretty=0):
	if isTitle:
		font = BIGFONT
	elif isMega:
		font = MEGAFONT
	elif isPretty:
		font = PRETTYFONT
	else: font = BASICFONT
	surf = font.render(text, 1, colour)
	rect = surf.get_rect()
	if centerPos:
		rect.center = centerPos
	else:
		rect.topleft = topLeftPos
	return (surf, rect)


def resourceText(text, topLeftPos):
	"""Generates and blits resource amount indicators"""
	x, y = topLeftPos
	textSurf, textRect = genText(text, (GAP, GAP), my.WHITE, 0, 0, 0)
	bgRect = pygame.Rect((x, y), (x + textRect.width + GAP, y + textRect.height + GAP))
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

	def update(self):
		# RESOURCE AMOUNTS
		i = 0
		currentWidth = 0
		for key in my.resources.keys():
			currentWidth += resourceText(str(key) + ': ' + str(my.resources[key]), (GAP * (i + 1) + currentWidth, GAP))
			i += 1



class Button:
	"""A button, can be clickable, can have tooltip. When clicked, self.isClicked=True"""
	def __init__(self, text, style, screenPos, isClickable=0, isTitle=0, screenPosIsTopRight=0, tooltip=None):
		self.text, self.style, self.screenPos, self.isClickable, self.posIsTopRight = \
		(text, style, screenPos, isClickable, screenPosIsTopRight)
		if isTitle:
			self.textSurf = BIGFONT.render(self.text, 1, my.LIGHTGREY)
		else:
			self.textSurf = BASICFONT.render(self.text, 1, my.WHITE)
		# CREATE BASIC SURF
		self.padding = 6 # will be controlled by 'style' eventually
		self.buttonSurf = pygame.Surface((self.textSurf.get_width() + self.padding,
										  self.textSurf.get_height() + self.padding))
		self.buttonSurf.fill(my.BLUE)
		self.buttonSurf.blit(self.textSurf, (int(self.padding /2), int(self.padding /2)))
		self.currentSurf = self.buttonSurf
		self.rect = pygame.Rect(self.screenPos, self.buttonSurf.get_size())
		# CREATE ADDITIONAL SURFS
		if isClickable:
			# MOUSE HOVER
			self.hoverSurf = pygame.Surface(self.buttonSurf.get_size())
			self.hoverSurf.fill(my.RED)
			self.hoverSurf.blit(self.textSurf, (int(self.padding /2), int(self.padding /2)))
			# MOUSE CLICK
			self.clickSurf = pygame.Surface(self.buttonSurf.get_size())
			self.clickSurf.fill(my.DARKRED)
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
		if self.rect.collidepoint(userInput.mousePos):
			if userInput.mousePressed == True:
				self.currentSurf = self.clickSurf
			else:
				self.currentSurf = self.hoverSurf
				self.isHovered = True
		else:
			self.currentSurf = self.buttonSurf
		if userInput.mouseUnpressed == True and self.rect.collidepoint(userInput.mousePos):
			self.isClicked = True



class Tooltip:
	"""A multiline text box, displayed when isHovered=True"""
	def __init__(self, text, pos):
		self.pos = pos
		self.x, self.y = pos
		self.alpha = 0
		# GET TEXT OBJS
		self.textObjs, self.textHeight = self.genTextObjs(text)
		self.textWidth = self.getLongestTextLine(self.textObjs)
		# CREATE SURF
		self.surf = pygame.Surface((self.textWidth + GAP * 3, self.textHeight + GAP * 2))
		pygame.draw.rect(self.surf, my.CREAM, (GAP, 0, self.surf.get_width() - GAP, self.surf.get_height()))
		pygame.draw.polygon(self.surf, my.CREAM, [(0, 10), (GAP, 5), (GAP, 15)])
		for i in range(len(self.textObjs)):
			self.surf.blit(self.textObjs[i][0], self.textObjs[i][1])
		self.surf.set_colorkey(my.BLACK)
		

	def simulate(self, isHovered):
		if isHovered:
			if self.alpha < 255: self.alpha += 20
		elif self.alpha > 0:
			self.alpha -= 20
		if self.alpha > 0:
			self.surf.set_alpha(self.alpha)
			my.screen.blit(self.surf, self.pos)


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
		testText, testRect = genText(newText[0], (0, 0), my.BLACK, 0, 0, 0, 0)
		textHeight = testText.get_height()
		totalHeight = textHeight * (len(newText)) + GAP * (len(newText))
		for lineNum in range(len(newText)):
			surf, rect = genText(newText[lineNum], (GAP * 2, textHeight * lineNum + GAP * lineNum + GAP),
								 my.DARKGREY,0,0,0,0)
			textObjs.append([surf, rect])
		return textObjs, totalHeight


	def getLongestTextLine(self, textObjs):
		longestLineWidth = 0
		for i in range(len(textObjs)):
			if textObjs[i][1].width > longestLineWidth:
				longestLineWidth = textObjs[i][1].width
		return longestLineWidth
