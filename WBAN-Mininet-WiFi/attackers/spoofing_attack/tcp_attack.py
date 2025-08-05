import socket

def spoof_tcp(dest_ip, dest_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((dest_ip, dest_port))
        sock.sendall(b"Spoofed TCP data from fake IP")
        sock.close()
    except:
        pass

if __name__ == "__main__":
    spoof_tcp("10.0.0.253", 6003)
