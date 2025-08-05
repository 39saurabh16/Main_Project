import socket
import threading

def handle_client(client_sock, addr):
    print(f"New TCP connection from {addr}")
    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            print(f"Received TCP from {addr}: {data.decode()}")
    finally:
        client_sock.close()
        print(f"Closed TCP connection from {addr}")

def tcp_server(bind_ip='0.0.0.0', bind_port=6001):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((bind_ip, bind_port))
    sock.listen(5)
    print(f"TCP Server listening on {bind_ip}:{bind_port}")

    while True:
        client_sock, addr = sock.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    tcp_server()
