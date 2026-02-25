import dns.resolver

domain = "yachaytech.edu.ec"

answers_mx = dns.resolver.resolve(domain, 'MX')

for rdata in answers_mx:
    print(f"Priority: {rdata.preference} - Server: {rdata.exchange}")