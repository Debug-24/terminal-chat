"""
Message Router Module (Person B)
Handles message parsing, routing, and distribution
"""

import threading

# Dictionary to store connected clients: {username: socket}
clients = {}
clients_lock = threading.Lock()


def parse_command(message):
    """
    Parse message to identify commands
    Returns: (command_type, parsed_data)
    - command_type: 'pm', 'quit', 'broadcast', 'list', 'invalid'
    - parsed_data: dict with relevant info
    """
    message = message.strip()
    
    if message.startswith('/pm '):
        # Parse private message: /pm <username> <message>
        parts = message[4:].split(' ', 1)
        if len(parts) == 2:
            target_user, msg_content = parts
            return 'pm', {'target': target_user, 'message': msg_content}
        else:
            return 'invalid', {'error': 'Usage: /pm <username> <message>'}
    
    elif message.startswith('/quit'):
        return 'quit', {}
    
    elif message.startswith('/list'):
        return 'list', {}
    
    else:
        # Regular message - broadcast to all
        return 'broadcast', {'message': message}


def send_private_message(sender, target, message):
    """
    Send private message to specific user
    """
    with clients_lock:
        if target in clients:
            try:
                pm = f"[PM from {sender}] {message}"
                clients[target].sendall(pm.encode('utf-8'))
                # Confirm to sender
                clients[sender].sendall(f"[PM to {target}] {message}".encode('utf-8'))
                return True
            except Exception as e:
                print(f"Error sending PM: {e}")
                return False
        else:
            # User not found
            try:
                clients[sender].sendall(f"[ERROR] User '{target}' not found.".encode('utf-8'))
            except:
                pass
            return False


def broadcast_message(message, sender=None):
    """
    Broadcast message to all connected clients except sender
    """
    formatted_msg = f"[{sender}] {message}" if sender else message
    
    with clients_lock:
        disconnected = []
        for username, conn in clients.items():
            if username != sender:
                try:
                    conn.sendall(formatted_msg.encode('utf-8'))
                except:
                    disconnected.append(username)
        
        # Clean up disconnected clients
        for username in disconnected:
            print(f"[DISCONNECTED] {username} removed due to send error")
            clients[username].close()
            del clients[username]


def list_users(sender):
    """
    Send list of connected users to requesting client
    """
    with clients_lock:
        user_list = ", ".join(clients.keys())
        message = f"[USERS ONLINE] {user_list}"
        try:
            clients[sender].sendall(message.encode('utf-8'))
        except:
            pass


def route_message(sender, raw_message):
    """
    Main message router - routes messages based on command type
    This is the integration point Person A calls
    
    Args:
        sender: Username of the sender
        raw_message: Raw message string from client
    
    Returns:
        command_type: Type of command executed ('pm', 'broadcast', 'quit', etc.)
    """
    command_type, data = parse_command(raw_message)
    
    if command_type == 'pm':
        send_private_message(sender, data['target'], data['message'])
    
    elif command_type == 'broadcast':
        broadcast_message(data['message'], sender)
    
    elif command_type == 'list':
        list_users(sender)
    
    elif command_type == 'quit':
        return 'quit'  # Signal to disconnect
    
    elif command_type == 'invalid':
        with clients_lock:
            if sender in clients:
                try:
                    clients[sender].sendall(f"[ERROR] {data['error']}".encode('utf-8'))
                except:
                    pass
    
    return command_type


def add_client(username, conn):
    """
    Add a client to the clients dictionary (thread-safe)
    
    Returns:
        bool: True if added successfully, False if username taken
    """
    with clients_lock:
        if username in clients or not username:
            return False
        clients[username] = conn
        return True


def remove_client(username):
    """
    Remove a client from the clients dictionary (thread-safe)
    """
    with clients_lock:
        if username in clients:
            del clients[username]


def get_client_count():
    """
    Get the number of connected clients
    """
    with clients_lock:
        return len(clients)