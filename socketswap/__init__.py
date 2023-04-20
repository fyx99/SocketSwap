"""
SocketSwap

SocketSwap is a python package that allows to proxy any third-party libraries traffic through a local TCP Proxy
"""

__version__ = "0.1.0"
__author__ = 'fyx99'
__credits__ = 'No credits'

import socketswap.proxy 
from socketswap.proxy import start_local_proxy
from socketswap.context_manager import ProxySwapContext

__all__ = [
    socketswap.proxy,
    start_local_proxy,
    
    ProxySwapContext
]