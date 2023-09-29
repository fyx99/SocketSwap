"""
Demo Szenario - Connecting a postgres client via SocketSwap - redirect traffic locally

Setup: 
    docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=postgres postgres:latest
"""
import socket
import psycopg2
from SocketSwap import SocketSwapContext 


def socket_factory():
    target_host = "localhost"
    target_port = 5432
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def connect_postgres():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2222
    The socket_factory is provided to handle the creation of a socket to the remote target
    """
    
    with SocketSwapContext(socket_factory, [], "0.0.0.0", 2223):
        # Set up a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="postgres",
            user="postgres",
            password="password",
            port=2223
        )

        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute a SELECT query to retrieve data from a table
        cur.execute("SELECT CURRENT_TIMESTAMP;")

        # Fetch all the rows returned by the query
        rows = cur.fetchall()

        # Print the rows to the console
        for row in rows:
            print(row)  # prints the current_timestamp from the database

        # Close the cursor and connection
        cur.close()
        conn.close()






if __name__ == '__main__':
    # for testing
    connect_postgres()