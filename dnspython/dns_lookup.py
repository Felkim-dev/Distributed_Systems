import dns.resolver


hostname = "yachaytech.edu.ec"

try:
    # Type A record
    result = dns.resolver.resolve(hostname, 'A')
    print(f"IP address for {hostname}:")
    for ip_val in result:
        print(f"A Record: {ip_val.to_text()}")


except dns.resolver.NoAnswer:
    print(f"No A record found for {hostname}")
except Exception as e:
    print(f"An error ocurred: {e}")
