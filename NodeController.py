from APIServer import APIServer
from StoppableThread import StoppableThread
import time


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController(StoppableThread):
	
	def __init__(self, APISERVER, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER
		self.loopTime = LOOPTIME
	
	def run(self):
		while not self.stopped():
			with self.apiServer.etcdLock:
				for endpoint in self.apiServer.GetEndPoints():

					pod = self.apiServer.GetPod(endpoint)
					if pod.status == "FAILED":
						print("Restarting pod...")
						pod.status = "RUNNING"

					if not self.apiServer.CheckEndPoint(endpoint):
						print("Incorrect endpoint for", enpoint.node)
						#Find worker the pod is on and update endpoint
						for worker in self.apiServer.GetWorkers():
							pass

			time.sleep(self.loopTime)
		
		print("Node controller is finished.")
