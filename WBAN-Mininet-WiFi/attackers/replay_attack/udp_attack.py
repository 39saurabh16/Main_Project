import socket, time

# Sample replayed data (can be any type of payload)
replayed_data = [b'packet1', b'packet2', b'packet3']

def replay(dest_ip, dest_port, total_packets=15000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    count = 0
    while count < total_packets:
        for pkt in replayed_data:
            if count >= total_packets:
                break
            sock.sendto(pkt, (dest_ip, dest_port))
            count += 1
            time.sleep(0.0005)  # 0.5 ms delay to prevent CPU overload
    

if __name__ == "__main__":
    replay("10.0.0.253", 5005, total_packets=15000)
