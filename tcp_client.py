import socket

from rqst.ip import ip_header
from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header

from struct import *
import binascii

class TCPClient():
  def __init__(self, destination, data):
    self.dest_addr = '50.17.220.245'
    self.src_addr = '192.168.1.211'
    self.data = data
    self.connection = TCP_Connection()
    self.ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr).construct()

  def do_handshake(self):
    self.connection.new_connection(self.dest_addr)
    self.connection.connect()

    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1).construct()
    packet = self.ipheader + tcpheader

    getmore = True
    while getmore:
        self.connection.send(packet)
        q = self.connection.recv()
        print q.ip_header.src_adr
    '''
    wait for the syn/ack
    send an ack
    send the data
    receive the response
    '''

