import zmq
import time
import ldap
import ldap.modlist as modlist

# --- 1. Configuración LDAP ---
ldap_server = "ldap://localhost"
admin_dn = "cn=admin,dc=example,dc=com"
admin_pw = "yachay2026" # Tu clave de admin

# Configuramos la IP de tu máquina (Erick) y los puertos de los servicios
HOST = "172.23.210.60"
servicios = {
    "Peliculas": "15000",
    "ClimaHora": "15001",
    "InfoPersonal": "15002"
}

# Esta función representa las flechas P -> LDAP del diagrama
def registrar_servicio(nombre, ip, puerto):
    try:
        conn = ldap.initialize(ldap_server)
        conn.simple_bind_s(admin_dn, admin_pw)
        
        dn = f"uid={nombre},ou=People,dc=example,dc=com"
        
        # Mapeamos la tabla del profesor: Name | IP | PORT
        attrs = {
            'objectClass': [b'inetOrgPerson'],
            'uid': [nombre.encode('utf-8')],
            'cn': [nombre.encode('utf-8')],
            'sn': [ip.encode('utf-8')],          # Guardamos la IP aquí
            'description': [puerto.encode('utf-8')] # Guardamos el PORT aquí
        }
        
        try:
            ldif = modlist.addModlist(attrs)
            conn.add_s(dn, ldif)
            print(f"[LDAP] Servicio '{nombre}' registrado en -> IP: {ip}, PORT: {puerto}")
        except ldap.ALREADY_EXISTS:
            print(f"[LDAP] Servicio '{nombre}' ya estaba registrado en el directorio.")
            
    except Exception as e:
        print(f"Error LDAP: {e}")
    finally:
        conn.unbind_s()

# Registramos todos los servicios iterando el diccionario
print("Iniciando registro de servicios en LDAP...")
for nombre, puerto in servicios.items():
    registrar_servicio(nombre, HOST, puerto)

# --- 2. Configuración ZeroMQ (Publishers) ---
context = zmq.Context()

pub1 = context.socket(zmq.PUB)
pub1.bind("tcp://0.0.0.0:" + servicios["Peliculas"])

pub2 = context.socket(zmq.PUB)
pub2.bind("tcp://0.0.0.0:" + servicios["ClimaHora"])

pub3 = context.socket(zmq.PUB)
pub3.bind("tcp://0.0.0.0:" + servicios["InfoPersonal"])

print("\nPublishers transmitiendo...")
while True:
    time.sleep(5)
    pub1.send(b"[PELICULAS] Harry Potter")
    pub2.send(b"[CLIMA] Esta nublado")
    pub2.send((f"[HORA] {time.asctime()}").encode("utf-8"))
    pub3.send(b"[GITHUB] Felkim-dev")
    pub3.send(b"[LOCACION] Edificio Senescyt - Urcuqui")
