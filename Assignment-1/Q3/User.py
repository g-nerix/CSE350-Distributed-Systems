# import pika
# import sys
 
# def register_user(username):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue='user_requests')
    
#     message = f'{{"user": "{username}", "register": "True"}}'
#     print(f"Sent registeration request for the user name :{username}")
#     channel.basic_publish(exchange='', routing_key='user_requests', body=message)
#     # print("SUCCESS")
#     connection.close()

# def update_subscription(username, youtuber_name, action):
#     print(action == 's')
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue='user_requests')

#     if action in ('s', 'u'):
#         message = f'{{"user": "{username}", "youtuber": "{youtuber_name}", "subscribe": "{action == "s"}"}}'
#         print(f"SET subscription of youtuber '{youtuber_name}' to {action == 's'}")
#     else:
#         print("[FAIL] Inavlid action")
#         connection.close()
#         return

#     channel.basic_publish(exchange='', routing_key='user_requests', body=message)

#     print("SUCCESS")
#     connection.close()


# def receive_notifications(username):
#     def callback(ch, method, properties, body):
#         print(f"New Notification: {body.decode()}")

#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue=username)

#     channel.basic_consume(queue=username, on_message_callback=callback, auto_ack=True)

#     print(f"{username} is now receiving notifications...")
#     channel.start_consuming()

# if __name__ == '__main__':
#     # username = sys.argv[1]

#     # if len(sys.argv) > 2:
#     #     action = sys.argv[2]
#     #     if action == 's' or action == 'u':
#     #         youtuber_name = sys.argv[3]
#     #         subscribe = True if action == 's' else False
#     #         update_subscription(username, youtuber_name, subscribe)
#     #     elif action == 'r':
#     #         update_subscription(username)
#     # else:
#     #     receive_notifications(username)
#     username = "shashank"
#     youtuber_name = "TomScott"
#     subscribe = True
#     # username="djfvi"
#     # register_user(username)
#     update_subscription(username, youtuber_name,'s')
#     # update_subscription(username, youtuber_name,'u')
#     # receive_notifications("user_notifications")

import pika

class User:
    def __init__(self,name):
        self.username = name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='user_requests')
        

    def register_user(self):
        message = f'{{"user": "{self.username}", "register": "True"}}'
        print(f"Sent registration request for the username: {self.username}")
        self.channel.basic_publish(exchange='', routing_key='user_requests', body=message)
        print("SUCCESS")

    def update_subscription(self, youtuber_name, action):
        if action not in ('s', 'u'):
            print("[FAIL] Invalid action")
            return

        message = f'{{"user": "{self.username}", "youtuber": "{youtuber_name}", "subscribe": "{action == "s"}"}}'
        print(f"Set subscription of youtuber '{youtuber_name}' to {action == 's'}")
        self.channel.basic_publish(exchange='', routing_key='user_requests', body=message)
        print("SUCCESS")

    def receive_notifications(self):
        def callback(ch, method, properties, body):
            print(f"New Notification: {body.decode()}")

        self.channel.queue_declare(queue=self.username)
        self.channel.basic_consume(queue=self.username, on_message_callback=callback, auto_ack=True)

        print(f"{self.username} is now receiving notifications...")
        self.channel.start_consuming()

    def __del__(self):
        self.connection.close()

if __name__ == '__main__':
    
    # username = "shashank"
    username = "nerix"
    # username = "abcd"
    youtuber_name = "TomScott"
    subscribe = True
    user = User(username)
    # user.register_user()
    # user.update_subscription(youtuber_name, 's')
    # user.update_subscription(youtuber_name, 'u')
    user.receive_notifications()
