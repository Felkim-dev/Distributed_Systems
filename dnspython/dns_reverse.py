import dns.resolver

ip_address = "8.8.8.8"

try:

    answers = dns.resolver.resolve_address(ip_address)

    # Iterate over the answers and print the hostnames
    for rdata in answers:
        print(f"Hostname: {rdata.to_text()}")

except dns.resolver.NXDOMAIN:
    print(f"No domain name found for IP: {ip_address}")
except dns.resolver.NoNameservers:
    print(f"No nameservers available to resolve IP: {ip_address}")
except Exception as e:
    print(f"An error ocurred: {e}")
