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
    
    with ProxySwapContext(socket_factory, "127.0.0.1", 2222):
        # do something you want to proxy
        # connect to 127.0.0.1:2222

```
The ProxySwapContext takes essentially 3 mandatory arguments.  


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