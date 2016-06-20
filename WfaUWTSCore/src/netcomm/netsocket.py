###################################################################
#
# Copyright (c) 2016 Wi-Fi Alliance
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#
###################################################################

"""
Network communication APIs
"""

import socket
from select import select
import logging

class NetCommServer(object):

    """
    Parent class
    NetCommServer class variables
    """
    SOCK_READABLE = []
    SOCK_WRITABLE = []
    SOCK_ERROR = []
    SOCK_WAIT = []
    
    conntable = {}
    
    """
    Constructor for NetCommServer class
    sock_family can be either AF_INET or AF_INET6
    sock_type can be either SOCK_STREAM or SOCK_DGRAM
    """
    def __init__(self, sock_family, sock_type):
        """
        Initialize NetCommServer instance attributes
        """

        self.sock_family = sock_family
        self.sock_type = sock_type
        """
        Socket creation / initialization
        """
        try:
            self.sock = socket.socket(self.sock_family, self.sock_type)
            #print "Socket created successfully..."
        except socket.error, (err_num, err_msg):
            #if self.sock:
                #self.sock.close()
            print "Socket creation error - ", err_num, ": ", err_msg

    def networkSockReuse(self):
        """
        Set network socket reuse address option
        """
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print "Socket option to reuse address set..."
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)
            #print "Network socket error - ", err_num, ": ", err_msg

    def networkSockBlocking(self, sock_blocking):
        """
        Use blocking or non-blocking sockets
        """
        try:
            self.sock.setblocking(sock_blocking)
            print "Socket option for blocking set..."
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockTimeout(self, sock_timeout):
        """
        Set specific network socket timeout
        """
        try:
            self.sock.settimeout(sock_timeout)
            #print "Socket timeout set..." + str(sock_timeout)
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockBind(self, tcp_host, tcp_port):
        """
        Bind network server socket
        """
        try:
            self.sock.bind((tcp_host, tcp_port))
            print "Socket bind successful..."
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockListen(self, num_clients):
        """
        Start network server socket listening
        """
        try:
            self.sock.listen(num_clients)
            print "Socket listen successful..."
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockSelectAccept(self):
        """
        Use Select to Accept network server socket connections
        """
        try:
            while True:
                NetCommServer.SOCK_READABLE = [self.sock]
                read_sock, write_sock, error_sock = select(NetCommServer.SOCK_READABLE, NetCommServer.SOCK_WRITABLE, NetCommServer.SOCK_ERROR, 0.1)
                if read_sock:
                    tcp_client_sock, tcp_client_addr = self.sock.accept()
                    print "Received connection from ", tcp_client_addr
                    break
                if write_sock or error_sock:
                    pass
            return tcp_client_sock
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockAccept(self):
        """
        Accept network server socket connections
        """
        try:
            tcp_client_sock, tcp_client_addr = self.sock.accept()
            print "Received connection from ", tcp_client_addr
            return tcp_client_sock
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockSelectRecvfrom(self, receive_buffer_size):
        """
        Receive UDP data from network socket using Select
        """
        try:
            while True:
                NetCommServer.SOCK_READABLE = [self.sock]
                read_sock, write_sock, error_sock = select(NetCommServer.SOCK_READABLE, NetCommServer.SOCK_WRITABLE, NetCommServer.SOCK_ERROR, 0.1)
                if read_sock:
                    data, UDP_client_addr = self.sock.recvfrom(receive_buffer_size)
                    #if data:
                        #print "Received connection from ", UDP_client_addr
                        #print "Data received - " + data
                if write_sock or error_sock:
                    pass
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockRecvfrom(self, receive_buffer_size):
        """
        Receive UDP data from network socket
        """
        try:
            data, UDP_client_addr = self.sock.recvfrom(receive_buffer_size)
            #if data:
            #    print "Received connection from ", UDP_client_addr
            #    print "Data received - " + data
            return data
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockSendto(self, UDP_client_addr, data):
        """
        Send UDP data to network socket
        """
        try:
            self.sock.sendto(data, UDP_client_addr)
            print "Data sent - " + data
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockSelectRecv(self, tcp_client_sock, receive_buffer_size):
        """
        Receive TCP data from network socket using Select
        """
        try:
            while True:
                NetCommServer.SOCK_READABLE = [self.sock]
                read_sock, write_sock, error_sock = select(NetCommServer.SOCK_READABLE, NetCommServer.SOCK_WRITABLE, NetCommServer.SOCK_ERROR, 0.1)
                if read_sock:
                    data = tcp_client_sock.recv(receive_buffer_size)
                    #if data:
                    #    logging.debug( "Data received - " + data)
                    return data
                if write_sock or error_sock:
                    pass
        except socket.error:
            print ""

    def networkSockRecv(self, tcp_client_sock, receive_buffer_size):
        """
        Receive TCP data from network socket
        """
        try:
            if self.sock:
                pass
            data = tcp_client_sock.recv(receive_buffer_size)
            #if data:
            #    logging.debug("Data received - " + data)
            return data
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockSend(self, tcp_client_sock, data):
        """
        Receive TCP data from network socket
        """
        try:
            if self.sock:
                pass
            tcp_client_sock.send(data)
            #print "Data sent - " + data
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

    def networkSockClose(self):
        """
        Terminate TCP/UDP server socket
        """
        try:
            if self.sock:
                self.sock.close()
            #print "Socket terminated..."
        except socket.error, (err_num, err_msg):
            raise Exception("Network socket error - ", err_num, ": ", err_msg)

class NetCommClient(NetCommServer):

    """
    Child class
    Constructor for NetCommClient class
    sock_family can be either AF_INET or AF_INET6
    sock_type can be either SOCK_STREAM or SOCK_DGRAM
    """
    def __init__(self, sock_family, sock_type):
        super(NetCommClient, self).__init__(sock_family, sock_type)

    def networkClientSockConnect(self, tcp_server_host, tcp_server_port):
        """
        Establish connection to network socket server
        """
        try:
            #print "===host:", tcp_server_host
            #print "===port", tcp_server_port
            self.sock.settimeout(10)

            self.sock.connect((tcp_server_host, int(tcp_server_port)))
            #print "Socket connect successful..."
            #logging.info('Connecting to - IP Addr = %s Port = %s', tcp_server_host, tcp_server_port)
            NetCommServer.SOCK_READABLE.append(self.sock)
            NetCommServer.SOCK_WAIT.append(self.sock)
            
        except socket.error, (err_num, err_msg):
            logging.error("TCP client socket error - %s: %s", str(err_num), err_msg)
            logging.error("Error connecting to %s:%s", tcp_server_host, tcp_server_port)


    def networkClientSockSelectRecvfrom(self, receive_buffer_size):
        """
        Receive UDP data from network socket using Select
        """
        super(NetCommClient, self).networkSockSelectRecvfrom(receive_buffer_size)

    def networkClientSockRecvfrom(self, receive_buffer_size):
        """
        Receive UDP data from network socket
        """
        super(NetCommClient, self).networkSockRecvfrom(receive_buffer_size)

    def networkClientSockSendto(self, UDP_client_addr, data):
        """
        Send UDP data to network socket
        """
        super(NetCommClient, self).networkSockSendto(UDP_client_addr, data)

    def networkClientSockSelectRecv(self, receive_buffer_size):
        """
        Receive TCP data from network socket using Select
        """
        tcp_client_sock = self.sock
        super(NetCommClient, self).networkSockSelectRecv(tcp_client_sock, receive_buffer_size)

    def networkClientSockRecv(self, receive_buffer_size):
        """
        Receive TCP data from network socket
        """
        tcp_client_sock = self.sock
        return super(NetCommClient, self).networkSockRecv(tcp_client_sock, receive_buffer_size)

    def networkClientSockSend(self, data):
        """
        Send TCP data to network socket
        """
        tcp_client_sock = self.sock
        super(NetCommClient, self).networkSockSend(tcp_client_sock, data)

    def networkClientSockClose(self):
        """
        Terminate TCP/UDP client socket
        """
        super(NetCommClient, self).networkSockClose()

    def networkClientSockTimeout(self, timeout):
        """
        Set specific network socket timeout
        """
        super(NetCommClient, self).networkSockTimeout(timeout)
