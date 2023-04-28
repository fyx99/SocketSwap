"""
Module to wrap the TCP proxy in a context manager daemon process
"""
import multiprocessing
import SocketSwap.proxy as proxy
import time
import logging
from logging.handlers import QueueListener

logger = logging.getLogger("SocketSwap")
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)


class SocketSwapContext:
    
    def __init__(self, *args):
        self.args = args
    
    def __enter__(self):
        logger.info("Starting Proxy Server")
        log_queue = multiprocessing.Queue()

        self.proxy_process = multiprocessing.Process(target=proxy.start_local_proxy, args=([log_queue, *self.args]))
        self.proxy_process.daemon = True
        self.proxy_process.start()
        log_queue_listener = QueueListener(log_queue, *logger.handlers)
        log_queue_listener.start()
        time.sleep(1)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        logger.info("Exiting proxy server")
        time.sleep(0.1)
        self.proxy_process.terminate()
        if exc_type:
            logger.error(str(exc_type))
            logger.error(str(exc_value))
            logger.error(str(traceback))
        

        