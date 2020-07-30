import Deployment
import EndPoint
from Etcd import Etcd
import Pod
import WorkerNode
import threading

#The APIServer handles the communication between controllers and the cluster. It houses
#the methods that can be called for cluster management

class APIServer():
	def __init__(self):
		self.etcd = Etcd()
		self.etcdLock = threading.Lock()
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

		#Create worker node
		workerNode = WorkerNode(info)

		#Add to node list
		self.GetWorkers().append(workerNode)
		
#	CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deploymentList
	def CreateDeployment(self, info):

		#Create deployment
		deployment = Deployment(info)

		#Add to deployment list
		self.GetDeployments().append(deployment)

#	RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(self, deploymentLabel):

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

#	CreateEndpoint creates an EndPoint object using information from a provided Pod and Node (worker) and appends it 
#	to the endPointList in etcd
	def CreateEndPoint(self, pod, worker):

		#Create endpoint
		endpoint = EndPoint(pod, pod.deploymentLabel, worker)

		#Add to endpoint list 
		self.GetEndPoints().append(endpoint)
	    
#	CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(self, endPoint):

		return endPoint.pod in endPoint.node.podList
	
#	GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deploymentLabel):

		#return the list of endpoints with a given deployment label
		return filter(lambda x: x.deploymentLabel == deploymentLabel, self.GetEndPoints())
	
#	CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deploymentLabel):

		#Get deployment
		deployment = next((x for x in self.GetDeployments() if x.deploymentLabel == deploymentLabel), None)

		#Create name
		deployment.currentReplicas += 1
		name = deploymentLabel + str(deployment.currentReplicas)

		#Create and add pod
		pod = Pod(name, deployment.cpuCost, 1, 1, 1, deploymentLabel)
		self.GetPending().append(pod)
	
#	GetPod returns the pod object stored in the internal podList of a WorkerNode
	def GetPod(self, endPoint):

		#Return the pod if it is in the node's pod lst otherwise None
		return next((x for x in endPoint.node.podList if endPoint.pod == x), None)
	
#	TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
#	No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
#	it will be deleted by the Kubelet
	def TerminatePod(self, endPoint):

		#Set the endpoint's pod status to 'TERMINATING'
		endPoint.pod.status = "TERMINATING"
	
#	CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
#	Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, depLabel):

		#Find the first pod in the deployment and fail it
		pod = next((x for x in self.GetRunning() if x.deploymentLabel == depLabel), None)
		if pod != None:
			pod.status = "FAILED"
	
#	AssignNode takes a pod in the pendingPodList and transfers it to the internal podList of a specified WorkerNode
#	It also adjust a worker's available cpu
	def AssignNode(self, pod, worker):

		#Assign pod
		self.GetPending().remove(pod)
		pod.status = "RUNNING"
		self.GetRunning().append(pod)
		worker.podList.append(pod)

		#Assign cpu usage
		worker.availabe_cpu -= pod.assigned_cpu

#	pushReq adds the incoming request to the handling queue	
	def pushReq(self, info):	
		self.etcd.reqCreator.submit(reqHandle, info)

#   Creates requests and notifies the handler of request to be dealt with
	def reqHandle(self, info):
		self.etcd.pendingReqs.append(Request(info))
		self.etcdLock.notify()
