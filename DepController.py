from APIServer import APIServer
from StoppableThread import StoppableThread
import time


#DepController is a control loop that creates and terminates Pod objects based on
#the expected number of replicas.
class DepController(StoppableThread):
	
	def __init__(self, APISERVER, LOOPTIME):
		StoppableThread.__init__(self)
		self.apiServer = APISERVER
		self.loopTime = LOOPTIME
	
	def run(self):
		while not self.stopped():
			with self.apiServer.etcdLock:
				
				#Check number of pods
				for deployment in self.apiServer.GetDeployments():
					replicasRequired = deployment.expectedReplicas - deployment.currentReplicas
					endpoints = self.apiServer.GetEndPointsByLabel(deployment.deploymentLabel)

					#Delete replicas if there are too many
					if replicasRequired < 0:
						replicasToDelete = -replicasRequired
						
						for i in range(0, replicasToDelete):
							#Don't go over the array
							if i < len(endpoints):
								endpoints[i].pod.status = "TERMINATING"
					
					#Create replicas if there are not enough
					elif replicasRequired > 0:
						for i in range(0, replicasRequired):
							self.apiServer.CreatePod(deployment.deploymentLabel)
							
			time.sleep(self.loopTime)
		print("Deployment controller stopped.")
