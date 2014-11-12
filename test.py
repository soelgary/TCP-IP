import time
from rqst.connection import TCP_Connection

c=TCP_Connection()
c.new_connection("fake")

for i in range(0,3):
    recv = c.recv()
    print recv
    time.sleep(1)

