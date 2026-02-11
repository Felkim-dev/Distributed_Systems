import zmq

context = zmq.Context()
s = context.socket(zmq.SUB)

HOST = 'localhost'
PORT = '15000'

p = "tcp://" + HOST + ":" + PORT
s.connect(p)

s.setsockopt_string(zmq.SUBSCRIBE, "TIME")

for i in range(5):
    time = s.recv().decode("utf-8")
    print(time)

