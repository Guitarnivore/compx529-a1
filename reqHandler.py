from APIServer import APIServer
from StoppableThread import StoppableThread

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler(StoppableThread):
	def __init__(self, APISERVER):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER
		self.requestsFailed = []
		self.requestsSucceeded = []

	def run(self):
		while not self.stopped():
			with self.apiServer.etcdLock: #Waits for notification of new request
				self.apiServer.etcdLock.wait_for(self.requestsWaiting)

				if not self.stopped():
					request = self.apiServer.GetPendingRequests()[0]
					del self.apiServer.GetPendingRequests()[0]

					endpoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
					if len(endpoints) > 0:
						print("Performing request...")
						if endpoints[0].pod.status == "RUNNING":
							endpoints[0].pod.HandleRequest(request.execTime)
							self.requestsSucceeded[len(self.apiServer.GetDeployments())-1] += 1
						else:
							self.requestsFailed[len(self.apiServer.GetDeployments())-1] += 1
							print("No running pod to perform request.")
					else:
						self.requestsFailed[len(self.apiServer.GetDeployments())-1] += 1
						print("No active endpoint to perform request.")

		print("Request handler stopped.")

	def requestsWaiting(self):
		#If stopped need to continue
		return len(self.apiServer.GetPendingRequests()) > 0 or self.stopped()
