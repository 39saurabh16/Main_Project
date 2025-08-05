import socket
import random
import time

def port_scan_attack(dest_ip, min_port=1, max_port=65535, total_packets=500000, delay=0.001):
    print(f"Starting port scan attack on {dest_ip} from port {min_port} to {max_port}")

    for _ in range(total_packets):
        port = random.randint(min_port, max_port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            sock.connect((dest_ip, port))
            print(f"[+] Port {port} is open")
            sock.close()
        except:
            pass
        time.sleep(delay)  # Optional: Add delay to simulate realistic attack

if __name__ == "__main__":
    port_scan_attack("10.0.0.253")
