
import socket
import sys

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((ip, port))
    if result == 0:
        print(f"✅ Success: Port {port} on {ip} is OPEN.")
    else:
        print(f"❌ Failure: Port {port} on {ip} is CLOSED/UNREACHABLE (Error: {result})")
    sock.close()

if __name__ == "__main__":
    ip = "100.102.18.75"
    port = 1433 # Default SQL Server port
    print(f"Testing connectivity to {ip}:{port}...")
    check_port(ip, port)
