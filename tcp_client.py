import socket, time

from rqst.ip import ip_header
from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.packet import Packet

from struct import *
import binascii
import datetime

class TCPClient():
  def __init__(self, destination, port, data):
    self.dest_addr = destination
    self.src_addr = '192.168.1.218'
    self.data = data
    self.port = port
    self.connection = TCP_Connection()
    self.ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr)

  def do_handshake(self):
    print "attempting handshake with %s %s %s" % (self.src_addr, self.dest_addr, 't')
    self.connection.new_connection(self.dest_addr, self.port)
    self.connection.connect()

    self.send_syn()
    
    syn_ack_packet = self.recv_syn_ack()
    if syn_ack_packet == None:
      print "timeout"
      exit()
    
    syn_ack_packet.pprint()

    self.send_ack(syn_ack_packet)
    self.send_data()    

    '''
    for i in range(0,10):
        print (socket.inet_ntoa(p.ip_header.src_adr), p.tcp_header.src_port,\
               socket.inet_ntoa(p.ip_header.dest_adr), p.tcp_header.dest_port)
        self.connection.send(pp)
    '''

    '''
    wait for the syn/ack
    send an ack
    send the data
    receive the response
    '''

  def send_data(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, seqn=2, payload=self.data)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    self.connection.send(pp)

  def send_ack(self, packet):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, ack=1, seqn=1, ackn=packet.tcp_header.seqn)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    print "ACK HERE"
    p.pprint()
    self.connection.send(pp)

  def send_syn(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    self.connection.send(pp)

  def recv_syn_ack(self):
    get_more = True
    start = datetime.datetime.now()
    while get_more:
      now = datetime.datetime.now()
      diff = now - start
      print diff.total_seconds()
      rec_packet = self.connection.recv()
      if rec_packet.ip_header.src_adr == self.dest_addr and rec_packet.tcp_header.syn and rec_packet.tcp_header.ack:
        return rec_packet
      elif diff.total_seconds() > 5:
        return None

