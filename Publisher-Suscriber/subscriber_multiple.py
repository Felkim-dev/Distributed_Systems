import zmq

context = zmq.Context()
s = context.socket(zmq.SUB)

IPs = {"STEVE": "172.23.198.53", "FELIPE": "172.23.198.121", "ERICK": "172.23.210.60"}

HOST = IPs["NOMBRE"] #CAMBIAR EL NOMBRE DEPENDIENDO LA IP

PORT1 = "15000"
PORT2 = "15001"
PORT3 = "15002"

p1 = "tcp://" + HOST + ":" + PORT1
p2 = "tcp://" + HOST + ":" + PORT2
p3 = "tcp://" + HOST + ":" + PORT3


# STEVE
# s.connect(p2)
# s.connect(p3)
# s.setsockopt_string(zmq.SUBSCRIBE, "[HORA]")
# s.setsockopt_string(zmq.SUBSCRIBE, "[LOCACION]")
# s.setsockopt_string(zmq.SUBSCRIBE, "[CLIMA]")

# for i in range(5):
#     message = s.recv().decode("utf-8")
#     print(message)

# ERICK
# s.connect(p2)
# s.connect(p1)
# s.setsockopt_string(zmq.SUBSCRIBE, "[HORA]")
# s.setsockopt_string(zmq.SUBSCRIBE, "[PELICULAS]")
# s.setsockopt_string(zmq.SUBSCRIBE, "[CLIMA]")

# for i in range(5):
#     message = s.recv().decode("utf-8")
#     print(message)

# FELIPE
# s.connect(p2)
# s.connect(p3)
# s.setsockopt_string(zmq.SUBSCRIBE, "[HORA]")
# s.setsockopt_string(zmq.SUBSCRIBE, "[GITHUB]")
# s.setsockopt_string(zmq.SUBSCRIBE, "[CLIMA]")

# for i in range(5):
#     message = s.recv().decode("utf-8")
#     print(message)
