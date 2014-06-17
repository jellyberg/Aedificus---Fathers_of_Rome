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
		#sliderData = [{'name': , 'range': ( , )}]
		self.testSlider1 = ui.Slider((400, 400), (10, 20), 'Number of pies', 13)


	def update(self):
		my.input.get()
		my.screen.fill(my.BLACK)

		self.testSlider1.update()

		my.FPSCLOCK.tick(my.FPS)
		pygame.display.update()



if __name__ == '__main__':
	run()