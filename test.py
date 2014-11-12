import rqst, time

c=rqst.TCP_Connection()
c.new_connection("fake")

for i in range(0,3):
    recv = c.recv()
    print 'great'
    print recv
    time.sleep(1)

