import socket, time

from rqst.ip import ip_header
from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.packet import Packet

from struct import *
import binascii
import datetime

class bcolors:
    HEADER = '\033[95m'
    WARN = '\033[1;93m'
    END = '\033[0m'
    @staticmethod
    def cprint(data):
        print "%s%s%s" % (bcolors.HEADER, str(data), bcolors.END)
    @staticmethod
    def wprint(data):
        print "%s%s%s" % (bcolors.WARN, str(data), bcolors.END)

class TCPClient():
  def __init__(self, destination, port, data):
    self.dest_addr = destination
    self.src_addr = socket.gethostbyname(socket.gethostname()) # get local ip
    self.data = data
    self.port = port

    self.connection = TCP_Connection().build_connection(self.dest_addr, self.port)

    self.ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr)
    self.timeout = 5

  def do_handshake(self):
    bcolors.cprint("attempting handshake with %s %s" % (self.src_addr, self.dest_addr))

    bcolors.cprint("sending syn packet")
    # what if the syn is dropped?
    self.send_syn()

    bcolors.cprint("attempting to recieve syn ack")
    syn_ack_packet = self.recv_syn_ack()

    if syn_ack_packet == None:
      print "timeout"
      exit()

    print syn_ack_packet
    bcolors.cprint("recieved")

    bcolors.cprint('sending ack')
    self.send_ack(syn_ack_packet)


    bcolors.cprint('begining packet capture')
    while True:
        new_packet = 1
        while new_packet is not None:
            new_packet = self.recv_data()


    bcolors.cprint('sending data')
    #self.send_data()

  def recv_data(self):
    start = datetime.datetime.now()
    while True:
      diff = datetime.datetime.now() - start
      rec_packet = self.connection.recv()
      if rec_packet.ip_header.src_adr == self.dest_addr:

        print rec_packet

        # recieved reset packet
        if rec_packet.tcp_header.rst == 1:
            bcolors.wprint("Recieved reset flag, something done goofed, i think this is because the local port is closed")
            return None

        return rec_packet
      elif diff.total_seconds() > self.timeout:
        return None

  def send_data(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            seqn=1, payload=self.data)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    print p
    self.connection.send(pp)

  def send_ack(self, packet):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            ack=1, seqn=1, ackn=packet.tcp_header.seqn)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    print p
    self.connection.send(pp)

  def send_syn(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    print p
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

