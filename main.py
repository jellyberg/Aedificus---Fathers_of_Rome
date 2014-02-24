import pygame, my, logic
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Real time strategy' + ' ' * 100 + 'FPS: ' + str(int(my.FPSCLOCK.get_fps())))

loadingScreen = pygame.image.load('assets/loadingScreen.png').convert_alpha()
my.screen.blit(loadingScreen, (0, 0))
pygame.display.update()

def main():
	runGame()


def runGame():
	handler = logic.Handler()
	while my.gameRunning:
		handler.update()
		


if __name__ == '__main__':
	main()