#!/usr/bin/env python3
"""
WBAN-WiFi testbed with explicit station associations and AP IP assignment
"""

from mn_wifi.net      import Mininet_wifi
from mn_wifi.node     import Station, OVSKernelAP
from mininet.node     import Controller, RemoteController
from mn_wifi.cli      import CLI
from mn_wifi.link     import wmediumd
from mn_wifi.wmediumdConnector import interference
from mininet.term import makeTerm  # <-- Required for xterm windows
import shutil
import signal
import os
import base64

def add_sensor(net, name, ip, pos, kind, udp_port, tcp_port):
    sta = net.addStation(
        name,
        ip=f"{ip}/24",
        position=pos,
        sensor_type=kind,
        udp_port=udp_port,
        tcp_port=tcp_port
    )
    return sta



def create_network():
    net = Mininet_wifi(
        controller=Controller,
        accessPoint=OVSKernelAP,
        link=wmediumd,
        wmediumd_mode=interference
    )

    print("*** Adding Wi-Fi AP and SDN controller")
    ap1 = net.addAccessPoint(
        'ap1',
        ssid='wban-net',
        mode='g',
        channel='1',
        position='45,45,0',
        ip='10.0.0.254/24'
    )
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    print("*** Adding 5 sensor stations")
    sensors = {
        'hr'  : ('10.0.0.1', '10,10,0', 'heart_rate', 5001, 6001),
        'tmp' : ('10.0.0.2', '12,15,0', 'temperature', 5002, 6002),
        'bp'  : ('10.0.0.3', '14,20,0', 'blood_pressure', 5003, 6003),
        'oxy' : ('10.0.0.4', '16,25,0', 'oxygen', 5004, 6004),
        'ecg' : ('10.0.0.5', '18,30,0', 'ecg', 5005, 6005),
    }
    for n, (ip, pos, kind, udp_port, tcp_port) in sensors.items():
        sta = add_sensor(net, n, ip, pos, kind, udp_port, tcp_port)
        sta.params['ssid'] = 'wban-net'

    print("*** Adding central server")
    srv = net.addStation('srv', ip='10.0.0.253/24', position='60,50,0')

    print("*** Adding attacker stations")
    attacker_ips = [
        ('atk1', '10.0.0.100', '30,30,0'),
        ('atk2', '10.0.0.101', '32,32,0'),
        ('atk3', '10.0.0.102', '34,34,0'),
        ('atk4', '10.0.0.103', '36,36,0'),
        ('atk5', '10.0.0.104', '38,38,0'),
    ]
    for name, ip, pos in attacker_ips:
        net.addStation(name, ip=f'{ip}/24', position=pos)

    print("*** Configuring Wi-Fi & links")
    net.setPropagationModel(model="logDistance", exp=4)
    net.configureWifiNodes()

    for sta in net.stations:
        net.addLink(sta, ap1)
        sta.setAssociation(ap1)

    print("*** Building & starting network")
    net.build()
    c0.start()
    ap1.start([c0])

    # ✅ Ensure logs folder exists
    os.makedirs("logs", exist_ok=True)

    print("*** Starting tcpdump on sensors and attackers")
    for sta in net.stations:
        if sta.name.startswith(("hr", "tmp", "bp", "oxy", "ecg", "atk")):
            net.terms.append(
                makeTerm(sta, cmd=f"tcpdump -i {sta.name}-wlan0 -w /tmp/{sta.name}.pcap")
            )

    # Helpful Legend
    print("\n=========== WBAN TESTBED READY ===========")
    for sta in net.stations:
        if hasattr(sta, 'sensor_type'):
            print(f" ▸ {sta.name:4}  {sta.IP():15}  {sta.sensor_type:14}")
        elif sta.name.startswith('atk'):
            print(f" ▸ {sta.name:4}  {sta.IP():15}  (attacker)")
        elif sta.name == 'srv':
            print(f" ▸ {sta.name:4}  {sta.IP():15}  (collector server)")
    print("==========================================\n")

    CLI(net)

    # # ====================== AFTER CLI EXIT ======================
    # print("*** Copying pcap files from nodes to host logs/ folder")
    # os.makedirs("logs", exist_ok=True)

    # for sta in net.stations:
    #     if sta.name.startswith(("hr", "tmp", "bp", "oxy", "ecg", "atk")):
    #         print(f"Copying {sta.name} pcap...")

    #         # Ensure pcap is inside shared /tmp
    #         sta.cmd(f"mv /tmp/{sta.name}.pcap /tmp/{sta.name}_final.pcap")

    #         # Now copy it from /tmp (host) to logs/ folder
    #         try:
    #             shutil.copy(f"/tmp/{sta.name}_final.pcap", f"logs/{sta.name}.pcap")
    #             print(f"Saved logs/{sta.name}.pcap")
    #         except FileNotFoundError:
    #             print(f"Warning: {sta.name}.pcap not found in /tmp/")

    # # Optional: kill leftover xterms safely
    # for term in net.terms:
    #     if hasattr(term, 'pid'):
    #         try:
    #             os.kill(term.pid, signal.SIGKILL)
    #         except Exception:
    #             pass
    net.terms = []

    net.stop()
    # print("*** Starting tcpdump on sensors and attackers")
    # for sta in net.stations:
    #     if sta.name.startswith("hr") or sta.name.startswith("tmp") or sta.name.startswith("bp") or \
    #        sta.name.startswith("oxy") or sta.name.startswith("ecg") or sta.name.startswith("atk"):
    #         net.terms.append(
    #             makeTerm(sta, cmd=f"tcpdump -i {sta.name}-wlan0 -w /tmp/{sta.name}.pcap")
    #         )

    # # ======= helpful legend =======
    # print("\n=========== WBAN TESTBED READY ===========")
    # for sta in net.stations:
    #     if hasattr(sta, 'sensor_type'):
    #         print(f" ▸ {sta.name:4}  {sta.IP():15}  {sta.sensor_type:14}")
    #     elif sta.name.startswith('atk'):
    #         print(f" ▸ {sta.name:4}  {sta.IP():15}  (attacker)")
    #     elif sta.name == 'srv':
    #         print(f" ▸ {sta.name:4}  {sta.IP():15}  (collector server)")
    # print("==========================================\n")

    # CLI(net)

    # print("*** Copying pcap files from nodes to host logs/ folder")
    # os.makedirs("logs", exist_ok=True)

    # for sta in net.stations:
    #     if sta.name.startswith(("hr", "tmp", "bp", "oxy", "ecg", "atk")):
    #         print(f"Copying {sta.name} pcap...")
    #         # This command copies the file from node’s /tmp to the host’s logs/ via mount namespace
    #         sta.cmd(f"cp /tmp/{sta.name}.pcap logs/{sta.name}.pcap")

    #         # Optional: check if it copied successfully
    #         if os.path.exists(f"logs/{sta.name}.pcap"):
    #             print(f"Saved logs/{sta.name}.pcap")
    #         else:
    #             print(f"Warning: {sta.name}.pcap not copied")
    # net.terms = []
    # net.stop()


# def create_network():
#     net = Mininet_wifi(
#         controller=Controller,
#         accessPoint=OVSKernelAP,
#         link=wmediumd,
#         # wmediumd_mode=None
#         wmediumd_mode=interference
#     )

#     print("*** Adding Wi-Fi AP and SDN controller")
#     ap1 = net.addAccessPoint(
#         'ap1',
#         ssid='wban-net',
#         mode='g',
#         channel='1',
#         position='45,45,0',
#         ip='10.0.0.254/24'    # Assign IP to AP for routing/debug
#     )
#     c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

#     print("*** Adding 5 sensor stations")
#     sensors = {
#         'hr'  : ('10.0.0.1', '10,10,0', 'heart_rate', 5001, 6001),
#         'tmp' : ('10.0.0.2', '12,15,0', 'temperature', 5002, 6002),
#         'bp'  : ('10.0.0.3', '14,20,0', 'blood_pressure', 5003, 6003),
#         'oxy' : ('10.0.0.4', '16,25,0', 'oxygen', 5004, 6004),
#         'ecg' : ('10.0.0.5', '18,30,0', 'ecg', 5005, 6005),
#     }
#     for n, (ip, pos, kind, udp_port, tcp_port) in sensors.items():
#         sta = add_sensor(net, n, ip, pos, kind, udp_port, tcp_port)
#         sta.params['ssid'] = 'wban-net'

#     print("*** Adding central server")
#     srv = net.addStation('srv', ip='10.0.0.253/24', position='60,50,0')

#     print("*** Adding attacker stations")
#     attacker_ips = [
#         ('atk1', '10.0.0.100', '30,30,0'),
#         ('atk2', '10.0.0.101', '32,32,0'),
#         ('atk3', '10.0.0.102', '34,34,0'),
#         ('atk4', '10.0.0.103', '36,36,0'),
#         ('atk5', '10.0.0.104', '38,38,0'),
#     ]
#     for name, ip, pos in attacker_ips:
#         net.addStation(name, ip=f'{ip}/24', position=pos)

#     print("*** Configuring Wi-Fi & links")
#     net.setPropagationModel(model="logDistance", exp=4)
#     net.configureWifiNodes()

#     # Associate all stations explicitly to the AP
#     for sta in net.stations:
#         net.addLink(sta, ap1)          # Add wireless link
#         sta.setAssociation(ap1)        # Force association to AP

#     print("*** Building & starting network")
#     net.build()
#     c0.start()
#     ap1.start([c0])

#     # Display summary
#     print("\n=========== WBAN TESTBED READY ===========")
#     for sta in net.stations:
#         if hasattr(sta, 'sensor_type'):
#             print(f" ▸ {sta.name:4}  {sta.IP():15}  {sta.sensor_type:14}")
#         elif sta.name.startswith('atk'):
#             print(f" ▸ {sta.name:4}  {sta.IP():15}  (attacker)")
#         elif sta.name == 'srv':
#             print(f" ▸ {sta.name:4}  {sta.IP():15}  (collector server)")
#         elif sta.name == 'ap1':
#             print(f" ▸ {sta.name:4}  {sta.IP():15}  (access point)")
#     print("==========================================\n")

#     CLI(net)
#     net.stop()


if __name__ == "__main__":
    create_network()


 