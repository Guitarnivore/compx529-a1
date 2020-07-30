import APIServer
from StoppableThread import StoppableThread

#The Scheduler is a control loop that checks for any pods that have been created
#but not yet deployed, found in the etcd pendingPodList.
#It transfers Pod objects from the pendingPodList to the runningPodList and creates an EndPoint object to store in the etcd EndPoint list
#If no WorkerNode is available that can take the pod, it remains in the pendingPodList
class Scheduler(StoppableThread):
	def __init__(self, APIServer, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APIServer
		
	def run(self):
		while True:
			if self.stopped():
				break
			with self.apiServer.etcdLock:
				#Go through the pending pods
				for pendingPod in self.apiServer.GetPending():

					#Find a node with room, if there is no room it will stay pending
					for node in self.apiServer.GetWorkers():
						if (node.available_cpu <= pendingPod.assigned_cpu):
							self.apiServer.AssignNode(pod, worker)
							
							#Create endpoint
							endpoint = EndPoint(pod, pod.deploymentLabel, worker)
							GetEndPoints().append(endpoint)
							break
