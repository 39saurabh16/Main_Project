import socket, time

replayed_data = [b'tcp_packet1', b'tcp_packet2', b'tcp_packet3']

def replay_tcp(dest_ip, dest_port):
    for pkt in replayed_data:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((dest_ip, dest_port))
            sock.sendall(pkt)
            sock.close()
            time.sleep(1)
        except:
            pass

if __name__ == "__main__":
    replay_tcp("10.0.0.253", 6005)
