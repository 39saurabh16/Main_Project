import socket
import time

def scan_ports(dest_ip, total_packets=200000):
    ports = list(range(5000, 5005))  # 10 ports
    num_ports = len(ports)
    iterations = total_packets // num_ports + 1

    sent_packets = 0
    for i in range(iterations):
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"probe", (dest_ip, port))
                sock.close()
                sent_packets += 1
                time.sleep(0.001)  # 1 ms delay for safety
                if sent_packets >= total_packets:
                    break
            except:
                continue
        if sent_packets >= total_packets:
            break

     

if __name__ == "__main__":
    scan_ports("10.0.0.253", total_packets=200000)

