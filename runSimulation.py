import threading
import time
from Request import Request
from DepController import DepController
from APIServer import APIServer
from reqHandler import ReqHandler
from NodeController import NodeController
from Scheduler import Scheduler
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 5
_depCtlLoop = 5
_scheduleCtlLoop = 5

apiServer = APIServer()
depController = DepController(apiServer, _depCtlLoop)
nodeController = NodeController(apiServer, _nodeCtlLoop)
reqHandler = ReqHandler(apiServer)
scheduler = Scheduler(apiServer, _scheduleCtlLoop)
reqHandler.start()
nodeController.start()
depController.start()
scheduler.start()

counter = 1
instructionNumber = []
numNodes = []
numDeployments = []
numRunningPods = []
numPendingPods = []

instructions = open("instructions.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])

			if len(apiServer.GetDeployments()) > len(reqHandler.requestsFailed):
				reqHandler.requestsSucceeded.append(0)
				reqHandler.requestsFailed.append(0)

		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			apiServer.RemoveDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'Sleep':
			time.sleep(int(cmdAttributes[1]))

		instructionNumber.append(counter)
		numNodes.append(len(apiServer.GetWorkers()))
		numDeployments.append(len(apiServer.GetDeployments()))
		numRunningPods.append(len(apiServer.GetRunning()))
		numPendingPods.append(len(apiServer.GetPending()))
		counter += 1

	time.sleep(5)

reqHandler.stop()
depController.stop()
scheduler.stop()
nodeController.stop()

#Display graph for requests failed
#https://matplotlib.org/3.3.0/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
def requestGraph():
	labels = []
	for i in range(1, len(reqHandler.requestsFailed)+1):
		labels.append(i)

	x = np.arange(len(labels))  # the label locations
	width = 0.35  # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(x - width/2, reqHandler.requestsSucceeded, width, label='Requests Succeeded')
	rects2 = ax.bar(x + width/2, reqHandler.requestsFailed, width, label='Requests Failed')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Requests')
	ax.set_title('Requests by number of deployments and success and failure rate')
	ax.set_xticks(x)
	ax.set_xticklabels(labels)
	ax.legend()


	def autolabel(rects):
		"""Attach a text label above each bar in *rects*, displaying its height."""
		for rect in rects:
			height = rect.get_height()
			ax.annotate('{}'.format(height),
						xy=(rect.get_x() + rect.get_width() / 2, height),
						xytext=(0, 3),  # 3 points vertical offset
						textcoords="offset points",
						ha='center', va='bottom')


	autolabel(rects1)
	autolabel(rects2)

	fig.tight_layout()

	plt.show()

#Display graph of overall run
def runStatsGraph():
	plt.plot(instructionNumber, numNodes, label='Number of Nodes')
	plt.plot(instructionNumber, numDeployments, label='Number of Deployments')
	plt.plot(instructionNumber, numRunningPods, label='Number of Running Pods')
	plt.plot(instructionNumber, numPendingPods, label='Number of Pending Pods')
	plt.legend()

	plt.title('Overall run of instructions')

	plt.show()

requestGraph()
runStatsGraph()

#Notify to finish the controller
with apiServer.etcdLock:
	apiServer.etcdLock.notify()
