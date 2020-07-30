import APIServer
import StoppableThread

#The Scheduler is a control loop that checks for any pods that have been created
#but not yet deployed, found in the etcd pendingPodList.
#It transfers Pod objects from the pendingPodList to the runningPodList and creates an EndPoint object to store in the etcd EndPoint list
#If no WorkerNode is available that can take the pod, it remains in the pendingPodList
class Scheduler(StoppableThread):
	def __init__(self, APIServer, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APIServer
		
	def run:
		while true:
			if self.stopped():
				break		
			with apiServer.etcdLock:

			time.sleep(LOOPTIME)
