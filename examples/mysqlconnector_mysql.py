"""
Demo Szenario - Connecting a MySQL  (pyodbc) client via SocketSwap - redirect traffic locally

Setup: 
    docker run --rm -d --name mysql-container -e MYSQL_ROOT_PASSWORD="soidfds98ihSDC§CWDc" -p 3306:3306 mysql:latest
    pip install mysql-connector-python
"""
import socket
import mysql.connector
from SocketSwap import SocketSwapContext 


def socket_factory():
    """factory"""
    target_host = "localhost"
    target_port = 3306
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def connect_mysql():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2222
    The socket_factory is provided to handle the creation of a socket to the remote target
    """
    
    with SocketSwapContext(socket_factory, [], "0.0.0.0", 2223):
        # Set up a connection to the mysql database
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=2223,
            user="root",
            password="soidfds98ihSDC§CWDc",
            database="mysql"
        )
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute a SELECT query to retrieve data from a table
        cur.execute("SELECT CURDATE();")

        # Fetch all the rows returned by the query
        rows = cur.fetchall()
        
        # Print the rows to the console
        for row in rows:
            print(row)
            

        # Close the cursor and connection
        cur.close()
        conn.close()
        

if __name__ == '__main__':
    # for testing
    connect_mysql()