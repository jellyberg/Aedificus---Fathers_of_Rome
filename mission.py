import my



class MoveCamera:
	def __init__(self):
		self.name = 'Move the camera'
		self.description = 'Use WASD keys or the mouse at the edge of the screen to pan the camera'
		self.startFocus = my.camera.focus

	def getProgress(self):
		if my.camera.focus != self.startFocus: return 100
		return 0


class RecruitOccupation:
	def __init__(self, occupation):
		self.name = 'Recruit a %s' %(occupation)
		self.description = "Use the '+' button next to the %s icon in the box on the mid-right\
							 of your screen convert one of your jobless labourers (wearing brown) \
							 to a %s. If you click the '-' button beside the %s icon it'll \
							 convert one of your builders to a labourer" %(occupation, occupation, occupation)
		self.occupation = occupation

	def getProgress(self):
		for human in my.allHumans:
			if human.occupation == self.occupation: return 100
		return 0


class BuildOrchard:
	def __init__(self):
		self.name = 'Build an orchard'
		self.description = 'Click the orchard icon on the bar at the bottom of the screen and \
							then click on a tile to place it. Make sure you have some builders!'

	def getProgress(self):
		if my.orchardHasBeenPlaced: return 100
		return 0


class ChopTrees:
	def __init__(self):
		self.name = 'Chop down 5 trees'
		self.description = 'Make sure you have a woodcutter, then click the tree icon in the top\
							 right of the screen and draw a box with the right mouse button to \
							 designate some trees'

	def getProgress(self):
		return my.treesChopped * 20


class BuildShed:
	def __init__(self):
		self.name = 'Build a shed'
		self.description = 'Click the shed icon on the bar at the bottom of the screen and \
							then click on a tile to place it. Make sure you have some builders!'

	def getProgress(self):
		if my.shedHasBeenPlaced: return 100
		return 0


class BuildBlacksmith:
	def __init__(self):
		self.name = 'Build a blacksmith'
		self.description = 'Click the blacksmith icon on the bar at the bottom of the screen and \
							then click on a tile to place it. Make sure you have some builders!'

	def getProgress(self):
		if my.blacksmithHasBeenPlaced: return 100
		return 0


class MineOre:
	def __init__(self):
		self.name = 'Mine some ore'
		self.description = 'Make sure you have a miner, then click the ore icon in the top\
							 right of the screen and draw a box with the right mouse button to \
							 designate some ore'

	def getProgress(self):
		for resource in ['coal', 'iron', 'gold']:
			if my.resources[resource] > 0: return 100
		return 0


class GrowPopulation:
	def __init__(self, targetPopulation):
		self.name = 'Grow your population to %s citizens' %(targetPopulation)
		self.description = 'Build huts to bear more citizens'
		self.targetPop = targetPopulation


	def getProgress(self):
		return int(len(my.allHumans) / self.targetPop * 100 )




class MissionTemplate:
	def __init__(self):
		self.name = ''
		self.description = ''

	def getProgress(self):
		return 0


def initMissions():
	my.currentMissionNum = 2
	my.MISSIONS = []
	my.MISSIONS.append(MoveCamera())
	my.MISSIONS.append(RecruitOccupation('builder'))
	my.MISSIONS.append(BuildOrchard())
	my.MISSIONS.append(RecruitOccupation('woodcutter'))
	my.MISSIONS.append(ChopTrees())
	my.MISSIONS.append(BuildShed())
	my.MISSIONS.append(BuildBlacksmith())
	my.MISSIONS.append(RecruitOccupation('miner'))
	my.MISSIONS.append(MineOre())
	my.MISSIONS.append(GrowPopulation(5))
	my.MISSIONS.append(GrowPopulation(20))
