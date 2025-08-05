import socket

def spoof(dest_ip, dest_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = b"Spoofed UDP data from fake IP"
    sock.sendto(msg, (dest_ip, dest_port))

if __name__ == "__main__":
    spoof("10.0.0.253", 5003)
