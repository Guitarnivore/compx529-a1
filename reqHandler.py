import APIServer
import StoppableThread

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler(StoppableThread):
	def __init__(self, APISERVER):
		Thread.__init__(self)
		self.apiServer = APISERVER

	def run():
		while true:
			if self.stopped():
				break
			with apiServer.etcdLock(): #Waits for notification of new request
				apiServer.etcdLock.wait()
