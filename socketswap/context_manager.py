"""
Module to wrap the TCP proxy in a context manager daemon process
"""
import multiprocessing
import SocketSwap.proxy as proxy
import time
import logging

logger = logging.getLogger("SocketSwap")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class SocketSwapContext:
    
    def __init__(self, *args):
        self.args = args
    
    def __enter__(self):
        logger.info("Starting Proxy Server")
        self.proxy_process = multiprocessing.Process(target=proxy.start_local_proxy, args=(self.args))
        self.proxy_process.daemon = True
        self.proxy_process.start()
        time.sleep(1)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        logger.info("Exiting proxy server")
        self.proxy_process.terminate()
        

        