import socket
import time
import argparse
import random

def main(dest_ip, dest_port, interval):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((dest_ip, dest_port))
    print(f"Connected to {dest_ip}:{dest_port} over TCP")

    try:
        while True:
            systolic = random.randint(110, 130)
            diastolic = random.randint(70, 85)
            message = f"blood_pressure:{systolic}/{diastolic}"
            sock.sendall(message.encode())
            print(f"Sent: {message}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest-ip", required=True)
    parser.add_argument("--dest-port", type=int, required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    main(args.dest_ip, args.dest_port, args.interval)
