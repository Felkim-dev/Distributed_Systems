import zmq, time

context = zmq.Context()

HOST = "0.0.0.0"

PORT1 = "15000"
PORT2 = "15001"
PORT3 = "15002"

# Publisher 1 - Servicio de Entretenimiento (puerto 15000)
pub1 = context.socket(zmq.PUB)
pub1.bind("tcp://" + HOST + ":" + PORT1)

# Publisher 2 - Servicio de Clima y Hora (puerto 15001)
pub2 = context.socket(zmq.PUB)
pub2.bind("tcp://" + HOST + ":" + PORT2)

# Publisher 3 - Servicio de Info Personal (puerto 15002)
pub3 = context.socket(zmq.PUB)
pub3.bind("tcp://" + HOST + ":" + PORT3)


print("Publisher escuchando a los subscribers...")
time.sleep(10)

while True:
    
    time.sleep(5)
    pub1.send(("[PELICULAS] Harry Potter").encode("utf-8"))
    time.sleep(5)
    pub2.send(("[CLIMA] Esta nublado").encode("utf-8"))
    time.sleep(5)
    pub2.send(("[HORA]" + time.asctime()).encode("utf-8"))
    time.sleep(5)
    pub3.send(("[GITHUB] Felkim-dev").encode("utf-8"))
    time.sleep(5)
    pub3.send(("[LOCACION] Edificio Senescyt - Urcuqui").encode("utf-8"))
