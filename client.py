"""
Terminal Chat Client
Connects to the chat server and allows users to send/receive messages
"""

import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 5000


def receive_messages(client_socket):
    """
    Continuously receive and display messages from the server
    Runs in a separate thread
    """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"\n{message}")
                print("> ", end="", flush=True)  # Re-display prompt
            else:
                print("\n[DISCONNECTED] Connection to server lost.")
                client_socket.close()
                break
        except OSError as e:
            if getattr(e, "winerror", None) == 10038:  # NEW: Windows socket closed error
                break
            break
        except Exception:
            break


def send_messages(client_socket):
    """
    Get user input and send messages to the server
    Runs in the main thread
    """
    try:
        while True:
            message = input("> ")
            
            if message:
                client_socket.sendall(message.encode('utf-8'))
                
                if message.strip() == '/quit':
                    print("[INFO] Disconnecting...")
                    break
    except KeyboardInterrupt:
        print("\n[INFO] Disconnecting...")
        client_socket.sendall('/quit'.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR) # NEW
        except:
            pass
        client_socket.close()


def start_client():
    """
    Connect to the chat server and start communication
    """
    try:
        # Create socket and connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        print(f"[CONNECTED] Connected to server at {HOST}:{PORT}\n")
        
        # Receive and respond to username prompt
        prompt = client.recv(1024).decode('utf-8')
        print(prompt, end="")
        username = input()
        client.sendall(username.encode('utf-8'))
        
        # Receive server response (welcome or error)
        response = client.recv(1024).decode('utf-8')
        print(response)
        
        # Check if connection was rejected
        if "Disconnecting" in response or "invalid" in response.lower():
            client.close()
            return
        
        # Start receiver thread for incoming messages
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        # NEW: Removed Daemon threads
        receive_thread.start()
        
        # Start sender in main thread (blocking)
        send_messages(client)

        # NEW: Wait for receiver thread to finish before exiting
        receive_thread.join()
        
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to server at {HOST}:{PORT}")
        print("[INFO] Make sure the server is running.")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("       TERMINAL CHAT CLIENT")
    print("=" * 50)
    start_client()
    print("\n[GOODBYE] Thanks for using Terminal Chat!")