import sys
import threading
import socket
import ssl
import select
import errno

proxy_socket = None

def is_valid_ip4(ip):
    # some rudimentary checks if ip is actually a valid IP
    octets = ip.split('.')
    if len(octets) != 4:
        return False
    return octets[0] != 0 and all(0 <= int(octet) <= 255 for octet in octets)


def receive_from(s):
    # receive data from a socket until no more data is there
    b = b""
    while True:
        data = s.recv(4096)
        b += data
        if not data or len(data) < 4096:
            break
    return b



def is_client_hello(sock):
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
        print("SSL handshake failed for listening socket", str(e))
        raise

    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if client_certificate and client_key:
            ctx.load_cert_chain(certfile=client_certificate,
                                keyfile=client_key,
                                )
        remote_socket = ctx.wrap_socket(remote_socket,
                                        server_hostname=sni,
                                        )
    except ssl.SSLError as e:
        print("SSL handshake failed for remote socket", str(e))
        raise

    return [remote_socket, local_socket]


def starttls(use_ssl, local_socket, read_sockets):
    return (use_ssl and
            local_socket in read_sockets and
            not isinstance(local_socket, ssl.SSLSocket) and
            is_client_hello(local_socket)
            )


def proxy_thread(connect_socket, local_socket, use_ssl, server_key, server_certificate, client_key, client_certificate):

    try:
        remote_socket = connect_socket()
    except socket.error as serr:
        if serr.errno == errno.ECONNREFUSED:
            for s in [remote_socket, local_socket]:
                s.close()
            print("connect socket - Connection refused")
            return None
        elif serr.errno == errno.ETIMEDOUT:
            for s in [remote_socket, local_socket]:
                s.close()
            print("connect socket - Connection timed out")
            return None
        else:
            for s in [remote_socket, local_socket]:
                s.close()
            raise serr
    
    running = True
    while running:
        read_sockets, _, _ = select.select([remote_socket, local_socket], [], [])

        if starttls(use_ssl, local_socket, read_sockets):
            try:
                ssl_sockets = enable_ssl(server_key, server_certificate, client_key, client_certificate, remote_socket, local_socket)
                remote_socket, local_socket = ssl_sockets
                print( "SSL enabled")
            except ssl.SSLError as e:
                print("SSL handshake failed", str(e))
                break

            read_sockets, _, _ = select.select(ssl_sockets, [], [])

        for sock in read_sockets:
            try:
                peer = sock.getpeername()
            except socket.error as serr:
                if serr.errno == errno.ENOTCONN:
                    # kind of a blind shot at fixing issue #15
                    # I don't yet understand how this error can happen, but if it happens I'll just shut down the thread
                    # the connection is not in a useful state anymore
                    for s in [remote_socket, local_socket]:
                        s.close()
                    running = False
                    break
                else:
                    print(f" Socket exception in start_proxy_thread")
                    raise serr

            data = receive_from(sock)
            print( 'Received %d bytes' % len(data))

            if sock == local_socket:
                if len(data):
                    print( b'< < < out\n' + data)
                    remote_socket.send(data.encode() if isinstance(data, str) else data)
                else:
                    print( "Connection from local client %s:%d closed" % peer)
                    remote_socket.close()
                    running = False
                    break
            elif sock == remote_socket:
                if len(data):
                    print( b'> > > in\n' + data)
                    local_socket.send(data)
                else:
                    print( "Connection to remote server %s:%d closed" % peer)
                    local_socket.close()
                    running = False
                    break
           


def start_local_proxy(connect_socket, local_host, local_port, server_key=None, server_certificate=None, client_key=None, client_certificate=None, use_ssl=False):
    
    print("hey")
    global proxy_socket
    if ((client_key is None) ^ (client_certificate is None)):
        print("You must either specify both the client certificate and client key or leave both empty")
        sys.exit(8)

    if local_host != '0.0.0.0' and not is_valid_ip4(local_host):
        try:
            ip = socket.gethostbyname(local_host)
        except socket.gaierror:
            ip = False
        if ip is False:
            print('%s is not a valid IP address or host name' % local_host)
            sys.exit(1)
        else:
            local_host = ip


    # local proxy socket
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        proxy_socket.bind((local_host, local_port))
    except socket.error as e:
        print(e.strerror)
        sys.exit(5)

    proxy_socket.listen(100)
    try:
        while True:
            in_socket, in_addrinfo = proxy_socket.accept()
            print( 'Connection from %s:%d' % in_addrinfo)
            pthread = threading.Thread(
                target=proxy_thread, 
                args=(connect_socket, in_socket, use_ssl, server_key, server_certificate, client_key, client_certificate)
            )
            print( "Starting proxy thread " + pthread.name)
            pthread.start()
    except KeyboardInterrupt:
        print( 'Ctrl+C detected, exiting...')
        sys.exit(0)


def stop_local_proxy():
    global proxy_socket
    try:
        if proxy_socket:
            proxy_socket.close()
    except:
        print("close exception")


if __name__ == '__main__':
    # for testing
    
    import socket
    

    def conn_factory():
        target_host = "localhost"
        target_port = 5432
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((target_host, target_port))
        return remote_socket
    
    start_local_proxy(conn_factory, "127.0.0.1", 2222)