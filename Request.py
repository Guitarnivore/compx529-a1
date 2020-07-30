#Requests stress Pod resources for a given period of time to simulate load
#deploymentLabel is the Deployment that the request is beings sent to
#cpuCost is the number of threads that the request will use on a pod
#duration is how long the request will use those resource for before completing
class Request():
	def __init__(self, INFOLIST):
		self.label = INFOLIST[0]
		self.deploymentLabel = INFOLIST[1]
		self.cpuCost = int(INFOLIST[2])
		self.execTime = int(INFOLIST[3])
