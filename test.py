import rqst, time
c=rqst.Connection()
c.new_connection("fake")

for i in range(0,10):
    recv = c.recv()
    time.sleep(1)

