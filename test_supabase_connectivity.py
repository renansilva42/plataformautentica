import socket
import ssl
import os
from urllib.parse import urlparse

def test_dns_and_connectivity(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

    print(f"Testing DNS resolution for hostname: {hostname}")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"DNS resolution successful: {hostname} -> {ip}")
    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")
        return False

    print(f"Testing TCP connection to {hostname}:{port}")
    try:
        sock = socket.create_connection((hostname, port), timeout=5)
        if parsed_url.scheme == 'https':
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=hostname)
        print(f"TCP connection successful to {hostname}:{port}")
        sock.close()
        return True
    except Exception as e:
        print(f"TCP connection failed: {e}")
        return False

if __name__ == "__main__":
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        print("SUPABASE_URL environment variable is not set.")
    else:
        success = test_dns_and_connectivity(supabase_url)
        if success:
            print("Connectivity test passed.")
        else:
            print("Connectivity test failed.")
