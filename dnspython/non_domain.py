import dns.resolver

non_existent_domain = "nonexistdomain12345.com"

try:
    # Attempt to resolve the non-existent domain
    print(f"Querying: {non_existent_domain}...")
    response = dns.resolver.resolve(non_existent_domain, "A")

except dns.resolver.NXDOMAIN:
    # This exception is raised when the DNS server returns an NXDOMAIN code
    print(f"Error: The domain '{non_existent_domain}' does not exist (NXDOMAIN).")

except dns.resolver.NoAnswer:
    # The domain exists, but the specific record type (A) does not
    print(f"Error: The domain exists but has no 'A' records.")

except dns.resolver.Timeout:
    # The distributed system failed to respond in time
    print("Error: The query timed out.")

except Exception as error:
    # Catch-all for any other issues
    print(f"An unexpected error occurred: {error}")
