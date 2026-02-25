import dns.resolver

domain = "yachaytech.edu.ec"

try:
    # 2. Query type 'SOA'
    answer_soa = dns.resolver.resolve(domain, "SOA")

    # Register SOA with many fields
    for rdata in answer_soa:
        print(f"--- Register SOA for {domain} ---")
        print(f"Master Server (MNAME): {rdata.mname}")
        print(f"Administrator Email (RNAME): {rdata.rname}")
        print(f"Serial Number (SERIAL): {rdata.serial}")
        print(f"Refresh Time (REFRESH): {rdata.refresh}s")
        print(f"Retry Time (RETRY): {rdata.retry}s")
        print(f"Expiration Time (EXPIRE): {rdata.expire}s")
        print(f"TTL Minimum (MINIMUM): {rdata.minimum}s")

except Exception as e:
    print(f"Error at the moment to obtain SOA register: {e}")
