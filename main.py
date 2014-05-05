# REAL TIME STRATEGY
# by Adam Binks   www.github.com/jellyberg/RTS

import pygame, my, logic, os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.mixer.pre_init(44100,-16,2, 1024)
pygame.init()
pygame.display.set_icon(pygame.image.load('assets/ui/icon.png'))
pygame.display.set_caption('Real time strategy')

my.screen.blit(my.loadingScreen, (0, 0))
pygame.display.update()

def main():
	runGame()


def runGame():
	handler = logic.Handler()
	while my.gameRunning:
		handler.update()


if __name__ == '__main__':
	main()