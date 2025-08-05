import socket, time

def flood(dest_ip, dest_port, duration=300):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'A' * 1024
    end = time.time() + duration
    while time.time() < end:
        sock.sendto(data, (dest_ip, dest_port))

if __name__ == "__main__":
    flood("10.0.0.253", 5001)
