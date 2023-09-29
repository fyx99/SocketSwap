"""
Demo Szenario - Connecting a TCP Socket via the SAP Cloud Connector socket

"""
from SocketSwap import SocketSwapContext 
from sapcloudconnectorpythonsocket import CloudConnectorSocket
import socket


def socket_factory(token):
    cc_socket = CloudConnectorSocket()
    cc_socket.connect(
        dest_host="virtualhost", 
        dest_port=3333, 
        proxy_host="connectivity-proxy", 
        proxy_port=20003, 
        token=token,
        location_id="CLOUD_CONNECTOR_LOCATION_ID"
    )
    return cc_socket

def connect_tcp_via_cloudconnectorsocket():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2223
    The socket_factory is provided to handle the creation of a socket to the remote target via the Cloud Connector
    """
    token = "<token>"
    
    with SocketSwapContext(socket_factory, [token], "127.0.0.1", 2223):
        # Set up a connection to the PostgreSQL database
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect(("127.0.0.1", 2223))

        remote_socket.send(b"")

        response = remote_socket.recv(4096)
        print(response) # Printe Hello TCP! from my local TCP server proxied via the dockerized proxy
            

if __name__ == '__main__':
    # for testing
    connect_tcp_via_cloudconnectorsocket()