from APIServer import APIServer
from StoppableThread import StoppableThread


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController(StoppableThread):
	
	def __init__(self, APISERVER, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER
	
	def run(self):
		while True:
			if self.stopped():
				break
			with self.apiServer.etcdLock:
				for worker in self.apiServer.GetWorkers():

					#Handle failed
					if worker.status == 'FAILED':
						worker.status = 'UP'

				#Check endpoints
				for endpoint in self.apiServer.GetEndPoints():
					if not self.apiServer.CheckEndPoint(endpoint):
						
						#Find worker the pod is on and update endpoint
						for worker in self.apiServer.GetWorkers():
							if (endpoint.pod in worker.podList):
								endpoint.node = worker
								break
