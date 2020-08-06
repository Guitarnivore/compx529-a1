import threading


#implements a stopping action to ensure that threads stop nicely
class StoppableThread(threading.Thread):

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def join(self):
        #Clear stop event so that join() means it continues to run.
        self._stop_event.clear()
        super.join()
