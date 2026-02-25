import dns.resolver

# Define the alias to be queried
target_alias = "www.microsoft.com"

try:
    # Perform the query for the 'CNAME' record type
    cname_response = dns.resolver.resolve(target_alias, "CNAME")

    print(f"--- Alias Resolution (CNAME) ---")

    for record in cname_response:
        # The 'target' attribute returns the actual name the alias points to
        print(f"The alias {target_alias} points to: {record.target}")

except dns.resolver.NoAnswer:
    print(f"The domain {target_alias} is not an alias (no CNAME record found).")
except Exception as e:
    print(f"Error: {e}")
