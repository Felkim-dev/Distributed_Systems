import dns.resolver


hostname = "yachaytech.edu.ec"

try:
    # Type A record
    result = dns.resolver.resolve(hostname, "NS")
    print(f"Server with authotity for {hostname}")
    
    for server in result:
        print(f"Nameserver: {server.target}")

except dns.resolver.NoAnswer:
    print(f"No A record found for {hostname}")
except dns.resolver.NXDOMAIN:
    print("Domain does not exists.")
except Exception as e:
    print(f"An error ocurred: {e}")
