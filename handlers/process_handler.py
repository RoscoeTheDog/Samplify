import multiprocessing
from handlers import database_handler


class NewHandler():

    def __init__(self):

        self.num_cores = multiprocessing.cpu_count()
        self.processes = []
        self.task_queues = []

        self.db = database_handler.NewHandler()

    def schedule_workers(self):

        for core in range(self.num_cores):

            # declare process, set daemon, add to list.
            p = multiprocessing.Process(target=self.consumer(),)
            p.daemon = True
            self.processes.append(p)

            # declare queue (listener) for process, add to list.
            q = multiprocessing.Queue()

            tracker = (p.name, q)
            self.task_queues.append(tracker)

            p.start()

    def consumer(self):

        p = multiprocessing.current_process()
        print(p.name)


handler = NewHandler()
handler.schedule_workers()

import time
time.sleep(30)
