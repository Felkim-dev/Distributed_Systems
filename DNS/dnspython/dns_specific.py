import dns.resolver

domain_name = "hpc.cedia.edu.ec"
dns_sv = '1.1.1.1'

resolver = dns.resolver.Resolver(configure=False)

resolver.nameservers = [dns_sv]

try:
    
    answers = resolver.resolve(domain_name,'A')
    
    print(f"Resolved IP addresses for {domain_name} using {dns_sv}")
    
    for rdata in answers:
        print(f"IP address using Cloudfare DNS: {rdata.address}")
        
except dns.resolver.NXDOMAIN:
    print(f"IP address not found for {domain_name}")
except Exception as e:
    print(f"An error ocurred: {e}")
