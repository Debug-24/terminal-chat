import socket
import threading

HOST = '127.0.0.1'  # localhost for initial testing
PORT = 5000         # Can change this if needed

# Dictionary to store connected clients: {username: socket}
clients = {}

# Broadcast message to all connected clients/users
def broadcast(message, sender=None):
    for username, conn in clients.items():
        if username != sender:  # Don't send to sender themselves
            try:
                conn.sendall(message.encode('utf-8'))
            except:
                conn.close()
                del clients[username]

# Handling messages from one client
def single_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    # Entering a username
    conn.sendall("Enter your username: ".encode('utf-8'))
    username = conn.recv(1024).decode('utf-8').strip()

    if username in clients:
        conn.sendall("Username already taken. Disconnecting.".encode('utf-8'))
        conn.close()
        return

    clients[username] = conn
    print(f"[ACTIVE] {username} joined the chat.")
    broadcast(f"[SERVER] {username} has joined the chat.", sender=username)
    conn.sendall("Welcome to TerminalChat! Type '/pm <user> <message>' to send private messages. And /quit to exit.\n".encode('utf-8'))

   