"""
Demo Szenario - Connecting a postgres client via SocketSwap
"""
import socket
import psycopg2
from socketswap import SocketSwapContext


def conn_factory():
    target_host = "localhost"
    target_port = 5432
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def connect_postgres():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2222
    The connection factory is provided to handle the creation of a socket to the remote target
    """
    
    with SocketSwapContext(conn_factory, "127.0.0.1", 2222):
        # Set up a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="postgres",
            user="postgres",
            password="password",
            port=2222
        )

        # ... postgres stuff