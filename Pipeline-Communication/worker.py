import zmq, time, pickle, sys

context = zmq.Context()
me = str(sys.argv[1])
r = context.socket(zmq.PULL)

HOST = 'localhost'
PORT1 = '13000'
PORT2 = '14000'

p1 = "tcp://" + HOST + ":" + PORT1
p2 = "tcp://" + HOST + ":" + PORT2

r.connect(p1)
r.connect(p2)

count = 1
while True:
    work = pickle.loads(r.recv())
    print(count)
    count += 1
    time.sleep(work[1] * 0.01)

