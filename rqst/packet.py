import socket
import itertools
import re
from struct import *
from rqst.tcp import tcp_header
from rqst.ip import ip_header


class Packet:
    """
      the Packet object encapsulates the TCP and IP
      layers by extracting raw data into appropriate header
      objects and providing a clean interface for construction
      of packets
    """
    def __init__(self, data=None,log=False):
        self.ip_header = None
        self.tcp_header = None
        self.ip_address = None
        self.header_size = 0
        self.data_size = 0

        if data is not None:
            self.parse(data)
        if log:
            self.pprint()

    def parse(self, data):
        """
           Parses tcp and ip headers from the packet
           allows access through objects fields
        """
        self.ip_address = data[1]
        self.ip_header = ip_header().parse(data[0])
        self.tcp_header = tcp_header().parse(data[0], self.ip_header.length)

        self.header_size = self.ip_header.length + self.tcp_header.length
        self.data_size = len(data[0]) - self.header_size
        self.raw_data = data[0][self.header_size:]

        return self

    def __str__(self):
        out = ""
        out += str(self.ip_header)
        out += "\n"
        out += str(self.tcp_header)
        out += "\n"
        return out

    def pprint(self):
      print self.ip_header
      print self.tcp_header

