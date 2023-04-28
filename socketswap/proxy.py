"""
Module to start a TCP proxy
"""
import sys
import threading
import socket
import ssl
import select
import errno
import logging
from logging.handlers import QueueHandler
from typing import Callable, List


logger = None
proxy_socket = None

def is_valid_ip4(ip):
    """Check if a string is a valid IPv4 address.

    Args:
        ip (str): A string representing an IPv4 address in the format "X.X.X.X".

    Returns:
        bool: True if the input string is a valid IPv4 address, False otherwise.

    Raises:
        None.

    This function splits the input string by periods and checks if it contains exactly 4 octets. It then verifies that each
    octet is an integer between 0 and 255 inclusive. Returns True if the input string is a valid IPv4 address, False otherwise.
    """
    octets = ip.split(".")
    if len(octets) != 4:
        return False
    return octets[0] != 0 and all(0 <= int(octet) <= 255 for octet in octets)


def receive_from(sock):
    """
    Receive data from a socket until no more data is available.

    Parameters:
    - sock (socket.socket): a socket object representing a network connection.

    Returns:
    - A bytes object containing all the data received from the socket.

    Notes:
    - This function receives data from the socket in chunks of 4096 bytes at a time, and concatenates them to a single bytes object.
    - The function stops receiving data from the socket when either the socket connection is closed or the last chunk of data received is less than 4096 bytes.
    - This function blocks until data is available from the socket or the socket is closed.

    Example:
    >>> import socket
    >>> sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    >>> sock.connect(("www.google.com", 80))
    >>> sock.sendall(b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n")
    >>> response = receive_from(sock)
    >>> print(response)
    b'HTTP/1.1 200 OK\r\nDate: Fri, 23 Apr 2023 22:12:17 GMT\r\nServer: gws\r\nContent-Type: text/html; charset=ISO-8859-1\r\n...
    """
    b = b""
    while True:
        data = sock.recv(4096)
        b += data
        if not data or len(data) < 4096:
            break
    return b


def is_client_hello(sock):
    """
    Check if a given socket contains a ClientHello message for SSL/TLS.

    Parameters:
    - sock (socket.socket): a socket object representing a network connection.

    Returns:
    - True if the socket's first bytes represent a ClientHello message for SSL/TLS, False otherwise.

    Notes:
    - This function does not consume any data from the socket, but only peeks at its first bytes with a maximum size of 128.
    - The function checks if the first byte is 0x16, which is the SSL/TLS handshake message type for ClientHello.
    - The function checks if the next two bytes represent the SSL/TLS protocol version and can be one of [b"\x03\x00", b"\x03\x01", b"\x03\x02", b"\x03\x03", b"\x02\x00"].

    Example:
    >>> import socket
    >>> sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    >>> sock.connect(("www.google.com", 443))
    >>> is_client_hello(sock)
    True
    """
    firstbytes = sock.recv(128, socket.MSG_PEEK)
    return (len(firstbytes) >= 3 and
            firstbytes[0] == 0x16 and
            firstbytes[1:3] in [b"\x03\x00",
                                b"\x03\x01",
                                b"\x03\x02",
                                b"\x03\x03",
                                b"\x02\x00"]
            )


def enable_ssl(server_key, server_certificate, client_key, client_certificate, remote_socket, local_socket):
    """
    Enable SSL/TLS encryption for a given connection.

    Parameters:
    - server_key (str): path to the private key file for the server-side SSL/TLS connection
    - server_certificate (str): path to the certificate file for the server-side SSL/TLS connection
    - client_key (str): path to the private key file for the client-side SSL/TLS connection (optional)
    - client_certificate (str): path to the certificate file for the client-side SSL/TLS connection (optional)
    - remote_socket (socket.socket): socket object representing the remote endpoint of the connection
    - local_socket (socket.socket): socket object representing the local endpoint of the connection

    Returns:
    - A list of two socket objects representing the wrapped remote and local sockets, respectively, with SSL/TLS encryption layers.

    Raises:
    - ssl.SSLError: if an SSL/TLS handshake error occurs during the setup process.
    """

    sni = None

    def sni_callback(sock, name, ctx):
        nonlocal sni
        sni = name

    try:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.sni_callback = sni_callback
        ctx.load_cert_chain(certfile=server_certificate,
                            keyfile=server_key,
                            )
        local_socket = ctx.wrap_socket(local_socket,
                                       server_side=True,
                                       )
    except ssl.SSLError as e:
        logger.error(f"SSL handshake failed for listening socket: {e}")
        raise

    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        if client_certificate and client_key:
            ctx.load_cert_chain(certfile=client_certificate, keyfile=client_key)
            
        remote_socket = ctx.wrap_socket(remote_socket, server_hostname=sni)
        
    except ssl.SSLError as e:
        logger.error(f"SSL handshake failed for remote socket: {e}")
        raise

    return [remote_socket, local_socket]


def starttls(use_ssl: bool, local_socket: socket.socket, read_sockets: List[socket.socket]) -> bool:
    """Check if a socket should start a TLS handshake (STARTTLS).

    Args:
        use_ssl (bool): A boolean indicating if STARTTLS should be used.
        local_socket (socket.socket): A local socket to be checked for the STARTTLS handshake.
        read_sockets (List[socket.socket]): A list of sockets that the server is listening to.

    Returns:
        bool: True if the local socket should start a TLS handshake, False otherwise.

    Raises:
        None.

    This function checks if the STARTTLS option is enabled, if the local socket is ready to read, if it is not already an
    SSL socket, and if it is sending a Client Hello message. If all conditions are met, the function returns True indicating
    that a STARTTLS handshake should be initiated.

    """
    return (use_ssl and
            local_socket in read_sockets and
            not isinstance(local_socket, ssl.SSLSocket) and
            is_client_hello(local_socket)
            )


def proxy_thread(socket_factory: Callable[[], socket.socket], local_socket: socket.socket, use_ssl: bool, server_key: str, server_certificate: str, client_key: str, client_certificate: str):
    """handles each connection read/write in a seperate thread"""
    try:
        remote_socket = socket_factory()
    except socket.error as socket_error:
        
        logger.error(f"SOCKET ERROR connecting remote socket: {socket_error}")
        local_socket.close()
            
        # TODO braucht man hier den noch? (errno.errorcode[errnumber], os.strerror(errnumber))
        if socket_error.errno not in (errno.ETIMEDOUT, errno.ECONNREFUSED):
            raise socket_error
        return None
        
    logger.info("Remote Socket connected successfully")
    
    running = True
    while running:
        read_sockets, _, _ = select.select([remote_socket, local_socket], [], [])

        if starttls(use_ssl, local_socket, read_sockets):
            try:
                ssl_sockets = enable_ssl(server_key, server_certificate, client_key, client_certificate, remote_socket, local_socket)
                remote_socket, local_socket = ssl_sockets
                logger.info("SSL enabled")
            except ssl.SSLError as e:
                logger.error(f"SSL handshake failed: {e}")
                break

            read_sockets, _, _ = select.select(ssl_sockets, [], [])

        for sock in read_sockets:
            try:
                peer = sock.getpeername()
            except socket.error as socket_error:
                if socket_error.errno == errno.ENOTCONN:
                    # kind of a blind shot at fixing issue #15
                    # I don't yet understand how this error can happen, but if it happens I'll just shut down the thread
                    # the connection is not in a useful state anymore
                    for s in [remote_socket, local_socket]:
                        s.close()
                    running = False
                    break
                else:
                    logger.info(f"Socket exception in start_proxy_thread")
                    raise socket_error

            data = receive_from(sock)
            logger.info(f"Received {len(data)} bytes")

            if sock == local_socket:
                if len(data):
                    logger.info( b'< < < out\n' + data)
                    remote_socket.send(data.encode() if isinstance(data, str) else data)
                else:
                    logger.info( "Connection from local client %s:%d closed" % peer)
                    remote_socket.close()
                    running = False
                    break
            elif sock == remote_socket:
                if len(data):
                    logger.info( b'> > > in\n' + data)
                    local_socket.send(data)
                else:
                    logger.info( "Connection to remote server %s:%d closed" % peer)
                    local_socket.close()
                    running = False
                    break
           


def start_local_proxy(log_queue, socket_factory, local_host, local_port, server_key=None, server_certificate=None, client_key=None, client_certificate=None, use_ssl=False):
    """starts a local proxy server"""
    global proxy_socket
    global logger
    
    logger = logging.getLogger("SocketSwapProxy")
    logger.addHandler(QueueHandler(log_queue))
    logger.setLevel(logging.DEBUG)
    
    logger.info("Starting local proxy server")
    
    if ((client_key is None) ^ (client_certificate is None)):
        logger.error("You must either specify both the client certificate and client key or leave both empty")
        sys.exit(8)

    if local_host != '0.0.0.0' and not is_valid_ip4(local_host):
        try:
            ip = socket.gethostbyname(local_host)
        except socket.gaierror:
            ip = False
        if ip is False:
            logger.error(f"Provided listening host is not a valid IP address or host name: {local_host}")
            sys.exit(1)
        else:
            local_host = ip


    # local proxy socket
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        proxy_socket.bind((local_host, local_port))
    except socket.error as e:
        logger.error(e.strerror)
        sys.exit(5)

    proxy_socket.listen(100)
    try:
        while True:
            in_socket, in_addrinfo = proxy_socket.accept()
            logger.info( 'Connection from %s:%d' % in_addrinfo)
            pthread = threading.Thread(
                target=proxy_thread, 
                args=(socket_factory, in_socket, use_ssl, server_key, server_certificate, client_key, client_certificate)
            )
            logger.info(f"Starting proxy thread {pthread.name}")
            pthread.start()
    except KeyboardInterrupt as e:
        logger.info(e)
        sys.exit(0)



def stop_local_proxy():
    """
    Stops the local proxy server by closing the listening socket.

    Note:
    This function uses a global variable proxy_socket to store the socket object. If proxy_socket is not defined
    or is already closed, no action will be taken.
    """
    global proxy_socket
    try:
        if proxy_socket:
            proxy_socket.close()
    except Exception as e:
        logger.error(f"Exception on closing listening socket: {e}")


if __name__ == '__main__':
    # for testing
    
    
    
    # logger = logging.getLogger("SocketSwap")
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.DEBUG)

    import socket
    

    def conn_factory():
        target_host = "localhost"
        target_port = 5432
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((target_host, target_port))
        return remote_socket
    
    start_local_proxy(conn_factory, "127.0.0.1", 2222)