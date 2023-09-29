"""
Demo Szenario - Connecting a TCP Socket via a SOCKS5 Proxy using PySocks

Setup: 
    pip install PySocks
    docker run -d -p 1080:1080 -e PROXY_USER=proxyuser -e PROXY_PASSWORD=password serjs/go-socks5-proxy
    running tcp server - node app-tcp.js https://gist.github.com/fyx99/cb6389e3c1942729cdbfc7ad3a9e1c71
"""
from SocketSwap import SocketSwapContext 
import socks
import socket


def socket_factory():
    target_host = "host.docker.internal"    # this is a stupid hack, because my tcp target is runing locally this equals to 127.0.0.1 in the docker container
    target_port = 4444
    proxy_host = "127.0.0.1"
    proxy_port = 1080
    remote_socket = socks.socksocket() 
    remote_socket.set_proxy(socks.SOCKS5, proxy_host, proxy_port, True, username="proxyuser", password="password")
    remote_socket.connect((target_host, target_port))
    return remote_socket

def connect_tcp_via_pysocks():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2223
    The socket_factory is provided to handle the creation of a socket to the remote target via the SOCKS5 proxy
    """
    
    with SocketSwapContext(socket_factory, [], "127.0.0.1", 2223):
        # Set up a connection to the PostgreSQL database
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect(("127.0.0.1", 2223))

        remote_socket.send(b"")

        response = remote_socket.recv(4096)
        print(response) # Printe Hello TCP! from my local TCP server proxied via the dockerized proxy
            

if __name__ == '__main__':
    # for testing
    connect_tcp_via_pysocks()