# message_server.py
import zmq
from group import GroupServer
address = "tcp://*:5555"
class MessagingAppServer:
    def __init__(self):
        self.groups = {}

    def handle_request(self, message):
        action = message.get("action")
        if action == "get_group_list":
            return {"status": "success", "groups": list(self.groups.keys())}
        elif action == "register_group":
            group_name = message.get("group_name")
            ip_address = message.get("ip_address")
            self.groups[group_name] = ip_address
            print(f"JOIN REQUEST FROM {message['ip_address']} [{ip_address}]")
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Invalid action"}


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(address)
    print(f"Server Started on {address}")
    server = MessagingAppServer()

    try:
        while True:
            try:
                message = socket.recv_json(flags=zmq.NOBLOCK)
                if message:
                    response = server.handle_request(message)
                    socket.send_json(response)
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
