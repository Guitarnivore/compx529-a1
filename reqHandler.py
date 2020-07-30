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
				self.apiServer.conditionLock.wait()

				for request in self.apiServer.GetPendingReqs():
					endpoints = GetEndPointsByLabel(request.deploymentLabel)
					requestPlaced = False

					#Block until the request is placed
					while not requestPlaced:
						for endpoint in endpoints:
							if endpoint.pod.available_cpu >= request.cpuCost:
								endpoint.pod.HandleRequest(request.execTime)
								self.apiServer.GetPendingReqs().remove(request)
								requestPlaced = True
