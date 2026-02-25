import ldap

ldap_server = "ldap://localhost"
ldap_username = "uid=erick,ou=People,dc=example,dc=com"
ldap_password = "yachay2026erick"

try:
    conn = ldap.initialize(ldap_server)
    conn.simple_bind_s(ldap_username, ldap_password)
    print("Authentication successful!")
except ldap.INVALID_CREDENTIALS:
    print("Authentication failed!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.unbind_s()
