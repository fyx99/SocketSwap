"""
SocketSwap

SocketSwap is a python package that allows to proxy any third-party libraries traffic through a local TCP Proxy
"""

__version__ = "0.1.0"
__author__ = 'fyx99'
__credits__ = 'No credits'

from SocketSwap.context_manager import SocketSwapContext
from SocketSwap.proxy import start_local_proxy


__all__ = [
    SocketSwapContext,
    start_local_proxy
]