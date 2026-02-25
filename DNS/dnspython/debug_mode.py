import dns.resolver

# Configuration for the debug query
target_domain = "yachaytech.edu.ec"

try:
    # 1. Perform the resolution
    result = dns.resolver.resolve(target_domain, 'A')

    # 2. Access the full DNS message object (the raw packet)
    dns_packet = result.response

    print(f"--- DEBUG MODE: FULL DNS MESSAGE FOR {target_domain} ---")

    # OP CODE and Flags (Shows if the response is authoritative, truncated, etc.)
    print(f"\n[HEADER INFO]")
    print(f"ID: {dns_packet.id}")
    print(f"Flags: {dns.flags.to_text(dns_packet.flags)}")

    # QUESTION SECTION: What we asked
    print("\n[QUESTION SECTION]")
    for question in dns_packet.question:
        print(f"-> {question.to_text()}")

    # ANSWER SECTION: The direct response to our query
    print("\n[ANSWER SECTION]")
    if dns_packet.answer:
        for answer in dns_packet.answer:
            print(f"-> {answer.to_text()}")
    else:
        print("No answer found.")

    # AUTHORITY SECTION: Which servers are responsible for this zone
    # This is crucial for understanding distributed delegation
    print("\n[AUTHORITY SECTION]")
    for authority in dns_packet.authority:
        print(f"-> {authority.to_text()}")

    # ADDITIONAL SECTION: Extra information like IP addresses of Name Servers (Glue Records)
    print("\n[ADDITIONAL SECTION]")
    for additional in dns_packet.additional:
        print(f"-> {additional.to_text()}")

except Exception as error:
    print(f"Debug Mode Error: {error}")
