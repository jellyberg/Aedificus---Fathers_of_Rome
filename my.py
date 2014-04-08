import pygame, random
from pygame.locals import *

DEBUGMODE = True
CHEATS = {'noHunger': 0, 'fastActions': 0, 'fastMoving': 0}

pygame.init()

FPS = 40
FPSCLOCK = pygame.time.Clock()

if DEBUGMODE:
	WINDOWWIDTH = 1080
	WINDOWHEIGHT = 720
	screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	loadingScreen = pygame.transform.scale(pygame.image.load('assets/ui/loadingScreen.png'), (WINDOWWIDTH, WINDOWHEIGHT))
if not DEBUGMODE:
	WINDOWWIDTH = 1920
	WINDOWHEIGHT = 1080
	screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), FULLSCREEN)
	loadingScreen = pygame.image.load('assets/ui/fullscreenLoadingScreen.png')
HALFWINDOWWIDTH = int(WINDOWWIDTH / 2)
HALFWINDOWHEIGHT = int(WINDOWHEIGHT / 2)


CELLSIZE = 20
HALFCELL = 10
MAPXCELLS = 200
MAPYCELLS = 200
MAPWIDTH = CELLSIZE * MAPXCELLS
MAPHEIGHT = CELLSIZE * MAPYCELLS
SCROLLACCEL = 1 # map scroll
SCROLLDRAG = 2 # bigger is less drag
MAPEDGEBOUNCE = 10
MAXSCROLLSPEED = 4

SUNMOVESPEED = 0.5
TREEFREQUENCY = random.randint(50, 100)   # 1/xth of tiles are trees
TREEMAXHEALTH = 400
WOODPERTREE = 50 # +/- a bit
NUMRIVERS = 30
NUMMOUNTAINS = 20
MASTEROREFREQ = 200
IRONFREQ = 2 # / MASTEROREFREQ of rock tiles
COALFREQ = 10 # / MASTEROREFREQ of rock tiles
MAXORESDESIGNATED = 30
MAXOREONFLOOR = 20


TREECHOPSPEED = 1
MAXTREESDESIGNATED = 30 # to help performance
OREMINESPEED = 1
CONSTRUCTIONSPEED = 3 # progress towards completion added per tick per builder
FISHFREQUENCY = 200 # lower is higher chance of fish per frame
FISHPERFISH = 100 # fish per Fish() caught by fishermen (+/- 20)
FISHCONSUMEDPERTICK = 0.2 # fish consumed per frame by each person eating at the fishmongers
MAXFISHONFLOOR = 10

STARTRESOURCES    = {'wood': 300, 'iron': 0, 'coal': 0, 'cheese': 250}
HUMANMOVESPEED = 2
STARTINGHAPPINESS = 20
STARTINGHUNGER = 1500
MAXHUNGER = 1500
FULLMARGIN = MAXHUNGER - 100
HUNGERWARNING = 800 # when people are not eating look for food
HUNGERURGENT = 300 # UH OH CRAZY HUNGRY NEED FOOD REAL QUICK
BUBBLEMARGIN = 3

if CHEATS['noHunger']:
	STARTINGHUNGER = 100000000000000000000000000000000000000
if CHEATS['fastActions']:
	TREECHOPSPEED = 100
	CONSTRUCTIONSPEED = 100
if CHEATS['fastMoving']:
	HUMANMOVESPEED = 10



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
BROWNBLACK= ( 50,  0,    0, 255)
CREAM     = (255, 255, 204, 255)
COLOURKEY = (  1,   2,   3, 255)
BLUETRANS = (  0,   0, 255, 100)


FIRSTNAMES = 'Robert Jenny Steve Jeff Alice Benjamin Yoric Fatima Reem Aya Suha Paul Becca Habiba \
				Mariam Irene Salma Liam Jacob Mohammed Ethan Cohen Jake Landon Elizabeth James John\
				Sophia Olivia Emma Brooklyn Ahmed Yusuf Chih-ming Chun-chieh Ji-hoon Abdullo Berat\
				Jim Catherine Earl Petunia Annabel Emily Nathan Jonathan Dylan Rachel Lucy Hannah\
				Jane Melissa Tabatha Willoughby Zanzibar Alexander Julius Atilla Mary Astrid Kylie\
				Josef Joseph Matilda Vladmir Charles Terence Lucifer Emmeline Elliot Marcus Julius\
				Helen Madeline Filius Caecilius Annia Alfidia Arria Atia Antonia Baebinia Claudia\
				Domitilla Domitia Euphemia Didia Clara Cornelia Davina Galla Helvia Hostia Julia\
				Justina Junia Gnaea Livia Minervina Orbinia Matidia Mucia Marcia Octavia Servilia\
				Terentia Turia Tullia Tranquilina Salonina Severa Vistillia Vesta Ulpia Violentilla\
				Vipsania Valeria Titus Sextus Lucius Flavius Amelius Iullus Apicius Arellius\
				Gaius Avienus Balista Decius Aufidius Aulus Tiberius Claudius Fannius Canius Spurius'.split()
LASTNAMES  = 'Prifti Loshi Leka Hoxha Gruber Huber Bauer Steiner Moser Jacobs Simon Martin Dupont\
				Dimitrov Trifonov Yanev Blagoev Hristov Yankov Novak Matic Hansen Magi Sepp Ilves\
				Koppel Parn Ilves Ivanov Pertov Putin Johannesen Thomsen Binks Rider Lehtonen Laine\
				David Garcia Morel Haynes Usher Martinez Francois Schmidt Schulz Wagner Hoffmann\
				Papantiniou Papadikas Nagy Toth Varga Mrphy Murray Jakupi Hoxha Sejdiu Borg Olsen\
				Berg Jacobsen Kozlov Kornilov Lenin Bogdanov Trotsky Nikolic Perez Reyes Armas Cruz\
				Smith Jones Wood Jackson Clarke Hall Green Roberts White Thompson Spoon Hall Green\
				Wright Robinson Wilson Taylor Khan Williams Roberts Lewis Cox Moore Kelly Rose Jenkins\
				Rees Driscoll Thomas Davies Edwards Reid MacDonald Robertson Clark Morrison Sanders'.split()