import socket
import threading

def udp_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    print(f"UDP Server listening on port {port}")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received on port {port} from {addr}: {data.decode()}")

ports = [5001, 5002, 5003, 5004, 5005]

threads = []
for port in ports:
    t = threading.Thread(target=udp_server, args=(port,), daemon=True)
    t.start()

print("UDP Servers running on all sensor ports.")
# Keep main thread alive
while True:
    pass



# import socket

# def udp_server(bind_ip='0.0.0.0', bind_port=5001):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind((bind_ip, bind_port))
#     print(f"UDP Server listening on {bind_ip}:{bind_port}")

#     while True:
#         data, addr = sock.recvfrom(1024)
#         print(f"Received UDP from {addr}: {data.decode()}")

# if __name__ == "__main__":
#     udp_server()
