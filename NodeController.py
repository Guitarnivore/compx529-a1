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

						#Put pod back pending
						pod.status = "PENDING"
						self.apiServer.GetPending().append(pod)
						self.apiServer.GetRunning().remove(pod)

						#Free up node resources
						endpoint.node.available_cpu += pod.assigned_cpu
						self.apiServer.GetEndPoints().remove(endpoint)

					if pod.status == "TERMINATING":

						print("Ending pod.")

						self.apiServer.GetRunning().remove(pod)

						pod.pool.shutdown()

						#Free up node resources
						endpoint.node.available_cpu += pod.assigned_cpu
						self.apiServer.GetEndPoints().remove(endpoint)

			time.sleep(self.loopTime)

		print("Node controller is finished.")
