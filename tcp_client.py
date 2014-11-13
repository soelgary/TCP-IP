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
    self.src_addr = socket.gethostbyname(socket.gethostname()) # get local ip
    self.data = data
    self.port = port
    self.connection = TCP_Connection()
    self.ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr)
    self.timeout = 5

  def do_handshake(self):
    print "attempting handshake with %s %s" % (self.src_addr, self.dest_addr)

    self.connection.new_connection(self.dest_addr, self.port)
    self.connection.connect()

    # what if the syn is dropped?
    self.send_syn()

    syn_ack_packet = self.recv_syn_ack()

    if syn_ack_packet == None:
      print "timeout"
      exit()

    print str(syn_ack_packet)

    self.send_ack(syn_ack_packet)
    self.send_data()

  def send_data(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            seqn=2, payload=self.data)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    self.connection.send(pp)

  def send_ack(self, packet):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            ack=1, seqn=1, ackn=packet.tcp_header.seqn)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    self.connection.send(pp)

  def send_syn(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    self.connection.send(pp)

  def recv_syn_ack(self):
    start = datetime.datetime.now()
    while True:
      diff = datetime.datetime.now() - start
      rec_packet = self.connection.recv()
      if rec_packet.ip_header.src_adr == self.dest_addr\
          and rec_packet.tcp_header.syn and rec_packet.tcp_header.ack:
        return rec_packet
      elif diff.total_seconds() > self.timeout:
        return None

