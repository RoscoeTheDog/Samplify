import multiprocessing
import structlog
from app.logging import custom_processors
import collections

logger = structlog.get_logger('samplify.log')


class NewHandler:

    def __init__(self):
        self.running_processes = []     # Note: 'process' objects are unpicklable
        self.decoder_channels = []

    # Pickling exclusions.
    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()

        # Remove the unpicklable entries
        del state['running_processes']
        return state

    def schedule_workers(self):

        num_cores = multiprocessing.cpu_count()

        logger.info('admin_message', msg='Spawning decoder processes', info=f'Num Cores: {num_cores}')

        for core in range(num_cores):

            # declare process, set daemon.
            p = multiprocessing.Process(target=self.schedule_listener, daemon=True)

            # declare double-ended channel (dequeue) for each process.
            q = collections.deque()

            # bundle channel and process name into a tuple
            channel_info = (p.name, q)

            # add to lists
            self.decoder_channels.append(channel_info)
            self.running_processes.append(p)

            # start process
            p.start()

    def schedule_listener(self):

        # return active working process
        p = multiprocessing.current_process()

        # get name/channel from list of channels
        for channel_info in self.decoder_channels:
            name, queue = channel_info

            # find the correct channel to work on
            if name == p.name:
                logger.info('admin_message', msg='Process started', info=f'Name: {name} PID: {p.pid} Queue: {queue}')

                # # start listening for signals
                while queue:
                    logger.info('admin_message', msg='Process started new task', info=f'Name: {name} PID: {p.pid} Task: {queue[0]}')
                    queue.popleft()

    # TODO: change algorithm to be more efficient at scheduling tasks
    def add_task(self, task):

        # Get process list.
        for p in self.running_processes:
            # Get channels list.
            for p_tasker in self.decoder_channels:
                name, queue = p_tasker

                # Add task to whichever process is currently not active.
                if not queue:
                    logger.info('admin_message', msg='Adding task to running process', info=f'Name: {name} PID: {p.pid} Task: {task}')
                    queue.appendleft(task)
                    break