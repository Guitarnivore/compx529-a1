from APIServer import APIServer
from StoppableThread import StoppableThread

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler(StoppableThread):
	def __init__(self, APISERVER):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER

	def run(self):
		while not self.stopped():
			with self.apiServer.etcdLock: #Waits for notification of new request
				self.apiServer.etcdLock.wait_for(self.requestsWaiting)

				request = self.apiServer.GetPendingRequests()[0]

				endpoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
				if len(endpoints) > 0:
					self.apiServer.GetPendingRequests().remove(request)
					print("Performing request...")
					endpoints[0].pod.HandleRequest(request.cpuCost, request.execTime)

		print("Request handler stopped.")

	def requestsWaiting(self):
		return len(self.apiServer.GetPendingRequests()) > 0
