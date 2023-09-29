# SocketSwap

SocketSwap is a tool that allows to proxy any third-party libraries traffic through a TCP SOCKS5 Proxy.

Some Python libaries support proxing out of the box like requests.
For all other libaries especially ones not natively written in python, you can use SocketSwap to redirect traffic via a proxy.

### Usage:

There are two ways to use SwapSock. 

    - Via a Context Manager that starts the proxy in a daemon process
    - Directly as a blocking script

#### Context Manager

```python 
import socket
from SocketSwap import ProxySwapContext


def socket_factory():
    target_host = "localhost"
    target_port = 5432
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((target_host, target_port))
    return remote_socket

def main():
    
    with ProxySwapContext(socket_factory, socket_factory_args, "127.0.0.1", 2222):
        # do something you want to proxy
        # connect to 127.0.0.1:2222

```
The ProxySwapContext takes essentially 4 mandatory arguments.  
The socket_factory - a function returning a socket.
The socket_factory_args - a iterable containing the arguments for the socket_factory.
The local_proxy_host - a host to bind for the local proxy typically localhost (127.0.0.1)
The local_proxy_port - a port to bind for the local proxy


#### Logging and Debugging
```python 
from SocketSwap import ProxySwapContext

# debug level logging
import logging
socket_swap_logger = logging.getLogger("SocketSwap")
socket_swap_logger.addHandler(logging.StreamHandler())
socket_swap_logger.setLevel(logging.DEBUG)

```
By default logging is not enabled. You can do so by assigning a handler to the "SocketSwap" logger and choosing a level.

## Credits:

The TCP Proxy part is a slim modified version of https://github.com/ickerwx/tcpproxy.