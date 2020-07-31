from Deployment import Deployment
from EndPoint import EndPoint
from Etcd import Etcd
from Pod import Pod
from WorkerNode import WorkerNode
from Request import Request
import threading

#The APIServer handles the communication between controllers and the cluster. It houses
#the methods that can be called for cluster management

class APIServer():
	def __init__(self):
		self.etcd = Etcd()
		self.etcdLock = threading.Condition()
		self.kubeletList = [] 
	
# 	GetDeployments method returns the list of deployments stored in etcd 	
	def GetDeployments(self):
		return self.etcd.deploymentList;
		
#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers(self):
		return self.etcd.nodeList;
		
#	GetPending method returns the list of PendingPods stored in etcd
	def GetPending(self):
		return self.etcd.pendingPodList;

#	GetRunning method returns the list of PendingPods stored in etcd
	def GetRunning(self):
		return self.etcd.runningPodList;
		
#	GetEndPoints method returns the list of EndPoints stored in etcd
	def GetEndPoints(self):
		return self.etcd.endPointList;

#	GetPendingRequests returns the list of pending requests.
	def GetPendingRequests(self):
		return self.etcd.pendingReqs
		
#	CreateWorker creates a WorkerNode from a list of arguments and adds it to the etcd nodeList
	def CreateWorker(self, info):
		print("Creating worker node...")

		#Create worker node
		workerNode = WorkerNode(info)

		#Add to node list
		self.GetWorkers().append(workerNode)

		print("Done. Current workers =", len(self.GetWorkers()), sep=' ')
		
#	CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deploymentList
	def CreateDeployment(self, info):
		print("Creating deployment...")

		#Create deployment
		deployment = Deployment(info)

		#Add to deployment list
		self.GetDeployments().append(deployment)
		
		print("Done. Current deployments =", len(self.GetDeployments()), sep=' ')

#	RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(self, deploymentLabel):
		print("Removing deployment...")

		#Get deployment
		deployment = next((x for x in self.GetDeployments() if x.deploymentLabel == deploymentLabel), None)
		#Return if the deployment doesn't exist
		if (deployment == None):
			return

		#Get all associated pods
		pods = filter(lambda x: x.deploymentLabel == deploymentLabel, self.GetRunning())
		pods.extend(filter(lambda x: x.deploymentLabel == deploymentLabel, self.GetPending()))

		#Remove deployment and set all pods to terminating
		self.GetDeployments().remove(deployment)
		for pod in pods:
			pod.status = "TERMINATING"

		print("Done. Current deployments =", len(self.GetDeployments()), sep=' ')

#	CreateEndpoint creates an EndPoint object using information from a provided Pod and Node (worker) and appends it 
#	to the endPointList in etcd
	def CreateEndPoint(self, pod, worker):
		print("Creating endpoint...")

		#Create endpoint
		endpoint = EndPoint(pod, pod.deploymentLabel, worker)

		#Add to endpoint list 
		self.GetEndPoints().append(endpoint)

		print("Done. Current endpoints =", len(self.GetEndPoints()), sep=' ')
	    
#	CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(self, endPoint):

		return True
	
#	GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deploymentLabel):

		#return the list of endpoints with a given deployment label
		return filter(lambda x: x.deploymentLabel == deploymentLabel, self.GetEndPoints())
	
#	CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deploymentLabel):
		print("Creating pod...")

		#Get deployment
		deployment = next((x for x in self.GetDeployments() if x.deploymentLabel == deploymentLabel), None)

		#Create name
		deployment.currentReplicas += 1
		name = deploymentLabel + str(deployment.currentReplicas)

		#Create and add pod
		pod = Pod(name, deployment.cpuCost, deployment.cpuCost, deploymentLabel)
		self.GetPending().append(pod)

		print("Done. Current pending pods =", len(self.GetPending()), sep=' ')
	
#	GetPod returns the pod object stored in the endPoint
	def GetPod(self, endPoint):

		return endPoint.pod
	
#	TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
#	No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
#	it will be deleted by the Kubelet
	def TerminatePod(self, endPoint):

		#Set the endpoint's pod status to 'TERMINATING'
		endPoint.pod.status = "TERMINATING"
	
#	CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
#	Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, depLabel):
		#Extract depLabel from array
		depLabel = depLabel[0]

		print("Crashing pod...")
		#Find the first pod in the deployment and fail it
		pod = next((x for x in self.GetRunning() if x.deploymentLabel == depLabel), None)
		
		if pod != None:
			pod.status = "FAILED"
			print("Crashed", pod.podName)
		else:
			print("No pods live to crash.")
	
#	AssignNode takes a pod in the pendingPodList and transfers it to the internal podList of a specified WorkerNode
#	It also adjust a worker's available cpu
	def AssignNode(self, pod, worker):
		print("Assigning", pod.podName, "to", worker.label, "...", sep=' ')

		#Assign pod
		self.GetPending().remove(pod)
		pod.status = "RUNNING"
		self.GetRunning().append(pod)

		print("Pending pod", pod.podName, "is now running. Total running pod =", len(self.GetRunning()))

		#Assign cpu usage
		worker.available_cpu -= pod.assigned_cpu

		print("Done.")

#	pushReq adds the incoming request to the handling queue	
	def PushReq(self, info):	
		self.etcd.reqCreator.submit(self.ReqHandle, info)

#   Creates requests and notifies the handler of request to be dealt with
	def ReqHandle(self, info):
		print("Appending request")
		request = Request(info)
		with self.etcdLock:
			self.GetPendingRequests().append(request)
			self.etcdLock.notify()
