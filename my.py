import pygame
from pygame.locals import *

pygame.init()

FPS = 60
FPSCLOCK = pygame.time.Clock()
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
HALFWINDOWWIDTH = int(WINDOWWIDTH / 2)
HALFWINDOWHEIGHT = int(WINDOWHEIGHT / 2)
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), DOUBLEBUF)


CELLSIZE = 20
MAPXCELLS = 200
MAPYCELLS = 200
MAPWIDTH = CELLSIZE * MAPXCELLS
MAPHEIGHT = CELLSIZE * MAPYCELLS
SCROLLACCEL = 1 # map scroll
SCROLLDRAG = 2 # bigger is less drag
MAPEDGEBOUNCE = 10
MAXSCROLLSPEED = 4


TREEFREQUENCY = 15   # 1/xth of tiles are trees
STARTRESOURCES    = {'wood': 100, 'iron': 10, 'cheese': 250}
STARTMAXRESOURCES = {'wood': 150, 'iron': 40, 'cheese': 250}
HUMANMOVESPEED = 2
CONSTRUCTIONSPEED = 3 # progress towards completion added per tick


# Colours     R    G    B  ALPHA
WHITE     = (255, 255, 255, 255)
BLACK     = (  0,   0,   0, 255)
RED       = (255,   0,   0, 255)
DARKRED   = (220,   0,   0, 255)
BLUE      = (  0,   0, 255, 255)
SKYBLUE   = (135, 206, 250, 255)
YELLOW    = (255, 250,  17, 255)
GREEN     = (  0, 255,   0, 255)
ORANGE    = (255, 165,   0, 255)
DARKGREEN = (  0, 155,   0, 255)
DARKGREY  = ( 60,  60,  60, 255)
LIGHTGREY = (180, 180, 180, 255)
BROWN     = (139,  69,  19, 255)
DARKBROWN = (100,  30,   0, 255)
BROWNBLACK= ( 50,  0,  0, 255)
CREAM     = (255, 255, 204, 255)
COLOURKEY = (  1,   2,   3, 255)