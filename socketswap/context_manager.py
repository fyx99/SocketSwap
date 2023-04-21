
import multiprocessing
from socketswap.proxy import start_local_proxy
import socket
import time


# def wrap_start_proxy(args):
#     start_local_proxy(*args)


class SocketSwapContext:
    
    def __init__(self, *args):
        self.args = args
    
    def __enter__(self):
        print("Starting Proxy Server")
        self.proxy_process = multiprocessing.Process(target=start_local_proxy, args=(self.args))
        self.proxy_process.daemon = True
        self.proxy_process.start()
        time.sleep(1)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting proxy server")
        self.proxy_process.terminate()
        

def conn_factory():
    target_host = "localhost"
    target_port = 5432
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

if __name__ == '__main__':
    # for testing
    
    
    with SocketSwapContext(conn_factory, "127.0.0.1", 2222):
        for i in range(1000):
            print(i)
            time.sleep(3)
        