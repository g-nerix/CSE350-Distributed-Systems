# user.py
import zmq
import uuid
import sys
import time

class UserClient:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.context = zmq.Context()
        self.socket_message_server = self.context.socket(zmq.REQ)
        self.socket_message_server.connect("tcp://localhost:5555")  # Connect to Message Server

        self.socket_group_server = self.context.socket(zmq.REQ)
        self.socket_group_server.connect("tcp://localhost:5556")  # Connect to Message Server

    def get_group_list(self):
        poller = zmq.Poller()
        poller.register(self.socket_message_server, zmq.POLLIN)

        self.socket_message_server.send_json({"action": "get_group_list"})
        socks = dict(poller.poll(timeout=1000))  # Timeout set to 1 second
        if self.socket_message_server in socks:
            response = self.socket_message_server.recv_json()
            if response["status"] == "success":
                groups = response["groups"]
                print("[MESSAGE SERVER] Available Groups:")
                for group in groups:
                    print("[MESSAGE SERVER]",group)
            else:
                print("[MESSAGE SERVER] Failed to get group list")
        else:
            print("[MESSAGE SERVER] Timeout: No response from server")

    def join_group(self, group_name):
        self.socket_group_server.send_json({"action": "join_group", "group_name": group_name, "user_id": self.id})
        response = self.socket_group_server.recv_json()
        if response["status"] == "success":
            print(f"[GROUP SERVER] Joined group: {group_name}")
        elif response["status"] == "error" and response["message"] == "User already in group":
            print("[GROUP SERVER] You are already part of the group.")
        else:
            print("[GROUP SERVER] Failed to join group")

    def leave_group(self, group_name):
        try:
            self.socket_group_server.send_json({"action": "leave_group", "group_name": group_name, 'user_id':self.id})
            response = self.socket_group_server.recv_json()
            if response["status"] == "success":
                print(f"[{self.name}] Left group {group_name}...")
            else:
                print(f"Failed to leave group: {group_name}")
        except zmq.error.ZMQError as e:
            print(f"Error occurred while leaving group: {e}")

    def send_message(self, group_name, message):
        self.socket_group_server.send_json({"action": "send_message", "group_name": group_name, "message": message, "user_id":self.id})
        response = self.socket_group_server.recv_json()
        print(f"[{self.name}] {message}")
        if response["status"] == "success":
            print("Message sent successfully")
        else:
            print("Failed to send message",response['message'])

    def get_messages(self, group_name, since_timestamp=None):
        self.socket_group_server.send_json({"action": "get_messages", "group_name": group_name, "since_timestamp": since_timestamp,"user_id":self.id})
        response = self.socket_group_server.recv_json()
        if response["status"] == "success":
            messages = response["messages"]
            print("Messages:")
            for message in messages:
                print(message)
        else:
            print("Failed to get messages",response['message'])
            
def work(name, group):
    user = UserClient(name)
    # Example usage:
    # user.get_group_list()  # Get available groups
    user.join_group(group)  # Join Group
    user.send_message(group, f"Hello, {group} {name} here")  # Send a message to Group
    # user.get_messages("Group 1")  # Get messages from Group1
    return user

def main():
    user_name = input("Enter username: ")
    user = UserClient(user_name)
    while True:
        print("\nMenu:")
        print("1. Get Group List")
        print("2. Join Group")
        print("3. Leave Group")
        print("4. Send Message")
        print("5. Get Messages")
        print("6. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            user.get_group_list()
        elif choice == "2":
            group_name = input("Enter group name to join: ")
            user.join_group(group_name)
        elif choice == "3":
            group_name = input("Enter group name to leave: ")
            user.leave_group(group_name)
        elif choice == "4":
            group_name = input("Enter group name to send message: ")
            message = input("Enter message: ")
            user.send_message(group_name, message)
        elif choice == "5":
            group_name = input("Enter group name to get messages: ")
            user.get_messages(group_name)
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")
    

if __name__ == "__main__":
    main()
   
    # user_A = work("USER_A", "Group 1")
    # time.sleep(2)
    # user_B = work("USER_B", "Group 1")
    # time.sleep(2)
    # user_C = work("USER_C", "Group 1")
    # time.sleep(2)
    # user_A.get_messages("Group 1")
    # user_C.leave_group("Group 1")
    # user_C.leave_group("Group 1")

