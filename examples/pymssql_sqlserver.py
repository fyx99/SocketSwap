"""
Demo Szenario - Connecting a MS SQL Server (pymssql) client via SocketSwap - redirect traffic locally

Setup: 
    docker run --rm -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Test@1i2bf34iuf3f3@WEDEWDw" -e "MSSQL_PID=Evaluation" -p 1433:1433  --name sqlpreview --hostname sqlpreview -d mcr.microsoft.com/mssql/server:2022-preview-ubuntu-22.04
    pip install pymssql
"""
import socket
import pymssql
from SocketSwap import SocketSwapContext 


def socket_factory():
    """factory"""
    target_host = "localhost"
    target_port = 1433
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def connect_sqlserver():
    """
    This function demos how to easily setup the local proxy using the SocketSwapContext-Manager.
    It exposes a local proxy on the localhost 127.0.0.1 on port 2222
    The socket_factory is provided to handle the creation of a socket to the remote target
    """
    
    with SocketSwapContext(socket_factory, [], "0.0.0.0", 2223):
        # Set up a connection to the sqlserver database
        conn = pymssql.connect(
            server="127.0.0.1:2223",
            user="sa",
            password="Test@1i2bf34iuf3f3@WEDEWDw",
            database="master"
        )
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute a SELECT query to retrieve data from a table
        cur.execute("SELECT GETDATE() AS CurrentTimestamp;")

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
    connect_sqlserver()