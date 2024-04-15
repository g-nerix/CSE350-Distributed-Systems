import zmq
import time
from datetime import datetime
import socket as sock
address = "tcp://*:5556" #change it as needed

class GroupServer:
    def __init__(self, group_name):
        self.group_name = group_name
        self.users = set()
        self.messages = []
        self.address = f"{sock.gethostname()}:5556"  # Get hostname and port for registration

    def register_with_message_server(self, message_server_address):
        try:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(message_server_address)

            socket.send_json({
                "action": "register_group",
                "group_name": self.group_name,
                "ip_address": self.address
            })

            response = socket.recv_json()
            if response["status"] == "success":
                print(f"[SUCCESS] registered Group : {self.group_name}")
            else:
                print("Failed to register with message server")
        except Exception as e:
            print(f"Error registering with message server: {e}")
        finally:
            socket.close()
            context.term()

    def join_group(self, user_id):
        if user_id in self.users:
            print(f"User {user_id} is already part of the group.")
            return False
        else:
            self.users.add(user_id)
            print(f"[{self.group_name}] JOIN REQUEST FROM [{user_id}]")
            return True

    def leave_group(self, user_id):
        if user_id in self.users:
            self.users.remove(user_id)
            print(f"User {user_id} left the group: {self.group_name}")
            return {"status": "success"}
        else:
            print(f"User {user_id} is not part of the group: {self.group_name}")
            return {"status": "error", "message": f"User {user_id} is not part of the group"}


    def send_message(self, user_id, message):
        # timestamp = str(datetime.now()).split(".")[0]
        timestamp = str(time.strftime("%H:%M:%S"))
        self.messages.append((timestamp, user_id, message))

    def get_messages(self, since_timestamp=None):
        if since_timestamp is None:
            return self.messages
        else:
            return [(ts, uid, msg) for ts, uid, msg in self.messages if ts >= since_timestamp]
        
def add_group(name,message_server_address,groups):
    group = GroupServer(name)
    group.register_with_message_server(message_server_address)
    groups[name] = group 

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(address)
    print(f"Server Started on {address}")
    
    groups = {}
    
    # adding groups and registering it
    message_server_address = "tcp://localhost:5555"
    add_group("Group 1",message_server_address,groups)
    add_group("Group 2",message_server_address,groups)
    add_group("Group 3",message_server_address,groups)
    
    try:
        while True:
            try:
                message = socket.recv_json(flags=zmq.NOBLOCK)
                if message:
                    action = message.get("action")
                    if action == "create_group":
                        group_name = message.get("group_name")
                        groups[group_name] = GroupServer(group_name)
                        socket.send_json({"status": "success"})

                    elif action == "join_group":
                        group_name = message.get("group_name")
                        
                        user_id = message.get("user_id")
                        
                        if group_name in groups:
                            groups[group_name].join_group(user_id)
                            socket.send_json({"status": "success"})
                        else:
                            socket.send_json({"status": "error", "message": "Group does not exist"})

                    elif action == "leave_group":
                        group_name = message.get("group_name")
                        user_id = message.get("user_id")
                        socket.send_json(groups[group_name].leave_group(user_id))
                        

                    elif action == "send_message":
                        group_name = message.get("group_name")
                        user_id = message.get("user_id")
                        message_content = message.get("message")
                        print(groups[group_name].users, user_id)
                        if group_name in groups:
                            if user_id in groups[group_name].users:
                                groups[group_name].send_message(user_id, message_content)
                                socket.send_json({"status": "success"})
                            else:
                                socket.send_json({"status": "error", "message": "User is not the part of the group"})
                        else:
                            socket.send_json({"status": "error", "message": "Group does not exist"})

                    elif action == "get_messages":
                        group_name = message.get("group_name")
                        since_timestamp = message.get("since_timestamp")
                        user_id = message.get("user_id")
                        if group_name in groups:
                            if user_id in groups[group_name].users:
                                messages = groups[group_name].get_messages(since_timestamp)
                                socket.send_json({"status": "success", "messages": messages})
                            else:
                                socket.send_json({"status": "error", "message": "User is not the part of the group"})
                        else:
                            socket.send_json({"status": "error", "message": "Group does not exist"})

                    else:
                        socket.send_json({"status": "error", "message": "Invalid action"})
                    
            except zmq.Again:
                # No message received within the timeout
                pass

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()
