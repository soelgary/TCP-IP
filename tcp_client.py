import socket, time

from rqst.ip import ip_header
from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.packet import Packet

from struct import *
import binascii

class TCPClient():
  def __init__(self, destination, port, data):
    self.dest_addr = destination
    self.src_addr = '192.168.1.211'
    self.data = data
    self.port = port
    self.connection = TCP_Connection()

  def do_handshake(self):
    print "attempting handshake with %s %s %s" % (self.src_addr, self.dest_addr, 't')
    self.connection.new_connection(self.dest_addr, self.port)
    self.connection.connect()

    ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr)
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1)

    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = ipheader
    pp = p.construct()

    for i in range(0,10):
        print (socket.inet_ntoa(p.ip_header.src_adr), p.tcp_header.src_port,\
               socket.inet_ntoa(p.ip_header.dest_adr), p.tcp_header.dest_port)
        self.connection.send(pp)


    getmore = True
    while getmore:
        q = self.connection.recv()
        if q.ip_header.src_adr == '104.131.119.105' or q.ip_header.dest_adr == '104.131.119.105':
            print q
    '''
    wait for the syn/ack
    send an ack
    send the data
    receive the response
    '''

