"""
Demo Szenario - Redirect traffic just locally

Setup:
    A TCP Hello World Server on Port 4444 example: https://gist.github.com/fyx99/cb6389e3c1942729cdbfc7ad3a9e1c71
"""
import socket
from SocketSwap import SocketSwapContext 

# debug level logging
import logging
socket_swap_logger = logging.getLogger("SocketSwap")
socket_swap_logger.addHandler(logging.StreamHandler())
socket_swap_logger.setLevel(logging.DEBUG)

def socket_factory():
    target_host = "localhost"
    target_port = 4444
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def basic_traffic_redirect():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2222
    The socket_factory is provided to handle the creation of a socket to the remote target
    """
    
    with SocketSwapContext(socket_factory, [], "127.0.0.1", 2222):
        # Set up a connection to the PostgreSQL database
        target_host = "127.0.0.1"
        target_port = 2222
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((target_host, target_port))
        
        remote_socket.send(b"")
        response = remote_socket.recv(4096)
        print(response)






if __name__ == '__main__':
    # for testing
    basic_traffic_redirect()