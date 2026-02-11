import zmq, time

context = zmq.Context()
s = context.socket(zmq.PUB)

HOST = 'localhost'
PORT = '15000'

p = "tcp://" + HOST + ":" + PORT
s.bind(p)

while True:
    time.sleep(5)
    s.send(("TIME " + time.asctime()).encode("utf-8"))

