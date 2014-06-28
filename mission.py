# AEDIFICUS: FATHERS OF ROME
# by Adam Binks   www.github.com/jellyberg/Aedificus---Fathers_of_Rome
# Read the devblog on Tumblr: bit.ly/Aedificus

import my, ui


class MoveCamera:
	def __init__(self):
		self.name = 'Move the camera'
		self.description = 'Use WASD keys or the mouse at the edge of the screen to pan the camera'
		self.startFocus = my.camera.focus
		my.defaultHungerLossRate = my.HUNGERLOSSRATE

	def getProgress(self):
		if 'blacksmith' in my.unlockedBuildings:
			my.unlockedBuildings.remove('blacksmith')

		my.HUNGERLOSSRATE = 0 # make the game a bit more forgiving for new players

		if my.camera.focus != self.startFocus: return 100
		return 0

	def onComplete(self):
		pass


class RecruitOccupation:
	def __init__(self, occupation):
		self.name = 'Recruit a %s' %(occupation)
		if occupation != 'jobless':
			self.description = "Convert a jobless labourer to a %s" %(occupation)
		if occupation == 'jobless':
			self.description = "Use the '-' button next to an occupation that one of your citizens does \
								to make him a labourer. Labourers carry items to storage buildings."
		self.occupation = occupation

	def getProgress(self):
		for human in my.allHumans:
			if human.occupation == self.occupation: return 100

		if self.occupation == 'jobless': return 0

		occupationNameOrder = [None, 'builder', 'woodcutter', 'miner', 'fisherman', 'blacksmith']
		isSecondColumn = occupationNameOrder.index(self.occupation) >= 3
		yValue = occupationNameOrder.index(self.occupation) % 3
		tip = ui.UItip((0, 0), 'Click the + button next to the %s' %(self.occupation))
		if tip in my.UItips: # if a new tip was created
			occAssRect = my.hud.occupationAssigner.rect
			tip.tooltip.rect.topright = (occAssRect.left + 28 * isSecondColumn - ui.GAP, occAssRect.top + yValue * 28 + ui.GAP*2)

		return 0

	def onComplete(self):
		pass


class BuildOrchard:
	def __init__(self):
		self.name = 'Build an orchard'
		self.description = 'Click the orchard icon on the bar at the bottom of the screen and \
							then click on a tile to place it. Make sure you have some builders!'

	def getProgress(self):
		try:
			my.HUNGERLOSSRATE = my.defaultHungerLossRate
		except NameError:
			my.HUNGERLOSSRATE = 20
		if my.orchardHasBeenPlaced: return 100

		# orchardButtonRect = my.hud.bottomBar.globalRects[2]
		# ui.UItip((orchardButtonRect.left - ui.GAP, orchardButtonRect.top), 'Build an orchard')

		return 0

	def onComplete(self):
		pass


class ChopTrees:
	def __init__(self):
		self.name = 'Chop down 5 trees'
		self.description = 'Make sure you have a woodcutter, then click the tree icon in the top \
							right of the screen and click and drag a box to designate some trees'

	def getProgress(self):
		return my.treesChopped * 20

	def onComplete(self):
		pass


class BuildShed:
	def __init__(self):
		self.name = 'Build a shed'
		self.description = 'Click the shed icon on the bar at the bottom of the screen and \
							then click on a tile to place it. Make sure you have some builders\
							and enough wood!'

	def getProgress(self):
		if my.shedHasBeenPlaced: return 100
		return 0

	def onComplete(self):
		my.unlockedBuildings.append('blacksmith')
		ui.StatusText('Blacksmith building unlocked!')


class BuildBlacksmith:
	def __init__(self):
		self.name = 'Build a blacksmith'
		self.description = 'Click the blacksmith icon on the bar at the bottom of the screen and \
							then click on a tile to place it. Make sure you have some builders\
							 and enough wood!'

	def getProgress(self):
		if my.blacksmithHasBeenPlaced: return 100
		return 0

	def onComplete(self):
		pass


class MineOre:
	def __init__(self):
		self.name = 'Mine some ore'
		self.description = 'Make sure you have a miner, then click the ore icon in the top\
							 right of the screen and click and drag a box  to designate some\
							 ore'

	def getProgress(self):
		for resource in ['coal', 'iron', 'gold']:
			if my.resources[resource] > 0: return 100
		return 0

	def onComplete(self):
		pass


class GrowPopulation:
	def __init__(self, targetPopulation):
		self.name = 'Grow your population to %s citizens' %(targetPopulation)
		self.description = 'Build huts to bear more citizens'
		self.targetPop = targetPopulation


	def getProgress(self):
		return int(len(my.allHumans) / self.targetPop * 100 )

	def onComplete(self):
		pass




class MissionTemplate:
	"""For easy copy and pasting"""
	def __init__(self):
		self.name = ''
		self.description = ''

	def getProgress(self):
		return 0

	def onComplete(self):
		pass


def initMissions(currentMissionNum):
	"""Set up mission order"""
	my.currentMissionNum = currentMissionNum
	my.mission = 'BLANK'
	my.MISSIONS = []
	my.MISSIONS.append(MoveCamera())
	my.MISSIONS.append(RecruitOccupation('builder'))
	my.MISSIONS.append(BuildOrchard())
	my.MISSIONS.append(RecruitOccupation('woodcutter'))
	my.MISSIONS.append(ChopTrees())
	my.MISSIONS.append(BuildShed())
	my.MISSIONS.append(GrowPopulation(5))
	my.MISSIONS.append(BuildBlacksmith())
	my.MISSIONS.append(RecruitOccupation('miner'))
	my.MISSIONS.append(MineOre())
	my.MISSIONS.append(GrowPopulation(20))
