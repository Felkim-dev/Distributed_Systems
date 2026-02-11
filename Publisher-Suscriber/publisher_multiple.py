import zmq, time

context = zmq.Context()
s = context.socket(zmq.PUB)

HOST = "localhost"
PORT = "15000"

p = "tcp://" + HOST + ":" + PORT
s.bind(p)

time.sleep(10)

while True:
    time.sleep(5)
    s.send(("[PELICULAS] Harry Potter").encode("utf-8"))
    time.sleep(5)
    s.send(("[CLIMA] Esta nublado").encode("utf-8"))
    time.sleep(5)
    s.send(("[HORA]" + time.asctime()).encode("utf-8"))
    time.sleep(5)
    s.send(("[GITHUB] Felkim-dev").encode("utf-8"))
    time.sleep(5)
    s.send(("[LOCACION] Edificio Senescyt").encode("utf-8"))
