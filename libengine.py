# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import pygame, my, logic, input, ui, os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.mixer.pre_init(44100,-16,2, 1024)
pygame.init()
pygame.display.set_icon(pygame.image.load('assets/ui/icon.png'))
pygame.display.set_caption('Aedificus: Fathers of Rome')

my.screen.blit(my.loadingScreen, (0, 0))
pygame.display.update()

my.gameRunning = False

def run():
	my.input = input.Input()
	menu = EmbarkMenu()
	while True:
		menu.update()

	if my.gameRunning:
		runGame()


def runGame():
	handler = logic.Handler()
	while my.gameRunning:
		handler.update()


class EmbarkMenu:
	def __init__(self):
		self.sliders = []
		self.sliderData = [{'label': 'Number of mountains', 'valRange': (5 , 20), 'default': 10},
							{'label': 'Number of rivers', 'valRange': (5 , 40), 'default': 20},
							{'label': 'Tree density', 'valRange': (50 , 150), 'default': 125}]
		i = 0
		for data in self.sliderData:
			self.sliders.append(ui.Slider((int(my.WINDOWWIDTH / 2 - ui.Slider.size[0] / 2), 200 + i*ui.Slider.size[1] + i*ui.GAP),
								 data['valRange'], data['label'], data['default']))
			i += 1


	def update(self):
		my.input.get()
		my.screen.fill(my.PASTELBLUE)

		for slider in self.sliders:
			value = slider.update()
			if slider.label == 'Number of mountains':
				my.NUMMOUNTAINS = value
			elif slider.label == 'Number of rivers':
				my.NUMRIVERS = value
			elif slider.label == 'Tree density':
				my.TREEFREQUENCY = 200 - value

		my.FPSCLOCK.tick(my.FPS)
		pygame.display.update()



if __name__ == '__main__':
	run()