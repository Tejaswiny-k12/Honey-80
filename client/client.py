# client.py
import socket
import threading
import sys

HOST = "127.0.0.1"  # if container is mapped to localhost
PORT = 4444

def recv_data(soc):
    while True:
        try:
            data = soc.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode(errors="ignore"))
            sys.stdout.flush()
        except:
            break

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((HOST, PORT))
    print(f"[+] Connected to {HOST}:{PORT}")

    threading.Thread(target=recv_data, args=(soc,), daemon=True).start()

    while True:
        try:
            cmd = input()
            soc.sendall((cmd + "\n").encode())
        except KeyboardInterrupt:
            print("\n[!] Exiting")
            soc.close()
            break

if __name__ == "__main__":
    main()