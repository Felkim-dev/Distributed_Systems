import zmq, time, pickle, sys, random

context = zmq.Context()
me = str(sys.argv[1])
s = context.socket(zmq.PUSH)

HOST = 'localhost'
PORT1 = '13000'
PORT2 = '14000'

PORT = PORT1 if me == '1' else PORT2
p = "tcp://" + HOST + ":" + PORT

s.bind(p)

for i in range(10):
    workload = random.randint(1, 100)
    s.send(pickle.dumps((me, workload)))

