import time
from rqst.connection import TCP_Connection

c=TCP_Connection()
c.new_connection("104.131.119.105",80)


for i in range(0,3):
    recv = c.recv()
    print recv

c.close()
