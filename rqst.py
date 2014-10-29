import socket
import itertools
import re
from struct import *


class Packet:
    def __init__(self):
        pass

    def new_packet(self, data):

        # Process IP Header
        ip_adr = data[1]
        packet = data[0]
        ip_hdr = packet[0:20]
        # unpack ip_head see:
        #   https://docs.python.org/2/library/struct.html#format-characters
        ip_header = unpack('!BBHHHBBH4s4s', ip_hdr)
        
        # extract version and header length
        v_hl = ip_header[0]
        version = v_hl >> 4
        ip_header_length = ((v_hl >> 4) *4)

        # extract ttl and protocol
        ttl = ip_header[5]
        protocol = ip_header[6]
        
        # get source and destination address
        src_adr = socket.inet_ntoa(ip_header[8])
        dest_adr = socket.inet_ntoa(ip_header[9])

        print "IP Header"
        print "Version: %s" % str(version)
        print "Length: %d" % ip_header_length
        print "TTL: %d" % ttl
        print "Protocol: %s" % str(protocol)
        print "Source address: %s" % str(src_adr)
        print "Destination address: %s" % str(dest_adr)

        # Process TCP Header

        # Extract TCP Header
        tcp_hdr = packet[ip_header_length:ip_header_length + 20]
        tcp_header = unpack('!HHLLBBHHH', tcp_hdr)

        # Get field
        source_port = tcp_header[0]
        dest_port = tcp_header[1]
        sequence = tcp_header[2]
        ack = tcp_header[3]
        doff_reserved = tcp_header[4]
        tcp_length = doff_reserved >> 4

        header_size = ip_header_length + tcp_length * 4
        data_size = len(paacket) - header_size

        raw_data = packet[h_size:]

        print "Data:"
        print raw_data


class Connection:
    def __init__(self):
        self.BUFFER_SIZE = (2**16)
    def new_connection(self,hostname):
        
        # set up raw socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        # get local ip
        self.host = socket.gethostbyname(socket.gethostname())

        self.port = 80
        self.buf = ""
        self.hostname = hostname

    def connect(self):
        try:
            self.sock.connect((self.hostname,self.port))
        except socket.gaierror as e:
            print("Recieved error when connecting to " + str((self.hostname, self.port)))
            raise e

    def close(self):
        self.sock.shutdown(1)
        self.sock.close()

    def send(self, data):
        print self.host
        self.sock.sendto(data,"50.17.220.245")

    def recv(self):
        self.buf = self.sock.recvfrom(65565)
        p = Packet()
        p.new_packet(self.buf)
        return self.buf
