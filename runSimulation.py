import threading
import time
from Request import Request
from DepController import DepController
from APIServer import APIServer
from reqHandler import ReqHandler
from NodeController import NodeController
from Scheduler import Scheduler

#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 0
_depCtlLoop = 0
_scheduleCtlLoop = 0

apiServer = APIServer()
depController = DepController(apiServer, _depCtlLoop)
nodeController = NodeController(apiServer, _nodeCtlLoop)
reqHandler = ReqHandler(apiServer)
scheduler = Scheduler(apiServer, _scheduleCtlLoop)
reqHandler.start()
nodeController.start()
depController.start()
scheduler.start()

instructions = open("instructions.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
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
	time.sleep(1)

reqHandler.stop()
depController.stop()
scheduler.stop()
nodeController.stop()

#Notify to finish the controller
with apiServer.etcdLock:
	apiServer.etcdLock.notify()
