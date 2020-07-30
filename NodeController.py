import APIServer
import StoppableThread


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController(StoppableThread):
	
	def __init__(self, APISERVER, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER
	
	def run(self):
		while true:
			if self.stopped():
				break
			with apiServer.etcdLock:

			time.sleep(LOOPTIME)
