import zmq
import ldap

# --- 1. Configuración LDAP ---
ldap_server = "ldap://localhost"
user_dn = "uid=erick,ou=People,dc=example,dc=com"
user_pw = "yachay2026erick" # Tu clave de usuario

# Esta función representa las flechas S -> LDAP del diagrama
def consultar_servicio(nombre_servicio):
    try:
        conn = ldap.initialize(ldap_server)
        conn.simple_bind_s(user_dn, user_pw)
        
        search_filter = f"(uid={nombre_servicio})"
        base_dn = "ou=People,dc=example,dc=com"
        result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        
        if result:
            dn, attrs = result[0]
            # Extraemos la IP y el PORT de la "tabla" de LDAP
            ip = attrs['sn'][0].decode('utf-8')
            puerto = attrs['description'][0].decode('utf-8')
            print(f"[LDAP] ÉXITO: El servicio '{nombre_servicio}' está en tcp://{ip}:{puerto}")
            return ip, puerto
        else:
            print(f"[LDAP] ERROR: Servicio '{nombre_servicio}' no encontrado.")
            return None, None
            
    except Exception as e:
        print(f"Error LDAP: {e}")
        return None, None
    finally:
        conn.unbind_s()

# --- 2. Ejecución de la Lógica del Subscriber ---

# Digamos que este subscriber quiere conectarse a "ClimaHora"
servicio_deseado = "ClimaHora"
print(f"Buscando '{servicio_deseado}' en el directorio LDAP...")

# 1. Consultamos LDAP (Flecha sólida S -> LDAP)
ip, puerto = consultar_servicio(servicio_deseado)

if ip and puerto:
    # 2. Conectamos ZeroMQ (Flecha punteada S -> P)
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    
    endpoint = f"tcp://{ip}:{puerto}"
    print(f"\nConectando Subscriber a ZeroMQ en {endpoint}...")
    sub.connect(endpoint)
    
    # Nos suscribimos a los tópicos de este servicio
    sub.setsockopt_string(zmq.SUBSCRIBE, "[HORA]")
    sub.setsockopt_string(zmq.SUBSCRIBE, "[CLIMA]")
    
    print("Escuchando mensajes...")
    for i in range(5):
        mensaje = sub.recv().decode("utf-8")
        print(mensaje)
