from APIServer import APIServer
from StoppableThread import StoppableThread

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler(StoppableThread):
	def __init__(self, APISERVER):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER

	def run(self):
		while True:
			if self.stopped():
				break
			with self.apiServer.etcdLock: #Waits for notification of new request
				self.apiServer.etcdLock.wait_for(self.requestsWaiting)

				print("Starting handle of request...")
				for request in self.apiServer.GetPendingRequests():
					endpoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
					requestPlaced = False

					for endpoint in endpoints:
						if endpoint.pod.available_cpu >= request.cpuCost:
							self.apiServer.GetPendingRequests().remove(request)
							print("Performing request...")
							endpoint.pod.HandleRequest(request.cpuCost, request.execTime)

	def requestsWaiting(self):
		return len(self.apiServer.GetPendingRequests()) > 0
