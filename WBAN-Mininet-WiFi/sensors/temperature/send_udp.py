import socket
import time
import argparse
import random

def main(dest_ip, dest_port, interval):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending UDP packets to {dest_ip}:{dest_port} every {interval}s")

    while True:
        sensor_value = random.uniform(36.0, 37.5)  # Body temperature °C
        message = f"temperature:{sensor_value:.1f}"
        sock.sendto(message.encode(), (dest_ip, dest_port))
        print(f"Sent: {message}")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest-ip", required=True)
    parser.add_argument("--dest-port", type=int, required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    main(args.dest_ip, args.dest_port, args.interval)
