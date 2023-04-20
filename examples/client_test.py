
import psycopg2

from socketswap import ProxySwapContext


def conn_factory():
    import socket
    target_host = "localhost"
    target_port = 5432
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def connect_postgres():
    
    with ProxySwapContext(conn_factory, "127.0.0.1", 2222):
        # Set up a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="postgres",
            user="postgres",
            password="password",
            port=2222
        )

        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute a SELECT query to retrieve data from a table
        cur.execute("SELECT CURRENT_TIMESTAMP;")

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
    connect_postgres()