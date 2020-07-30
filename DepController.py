import APIServer
import StoppableThread


#DepController is a control loop that creates and terminates Pod objects based on
#the expected number of replicas.
class DepController(StoppableThread):
	
	def __init__(self, APISERVER, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER
	
	def run(self):
		while true:
			if self.stopped():
				break
			with apiServer.etcdLock:
			    
			time.sleep(LOOPTIME)
