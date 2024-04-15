# import pika
# # import multiprocessing
# import threading

# subscriptions = {}
# users = {}
# running = True

# def consume_user_requests():
#     def callback(ch, method, properties, body):

#         global running
#         message = body.decode()
#         if message.lower() == 'stop':
#             running = False
#             return
     
#         message = message.split()
#         username = message[1][1:-2]
  
#         if len(message) == 4:
#             if message[3]:
#                 if username in users:
#                     print(f"[ERROR] : username '{username}' already exists, unable to register the user")
#                 else:
#                     users[username] =[]
#                     print(f"[SUCCESS] : Registered username '{username}'...")
#         elif len(message) == 6:
#             youtuber = message[3][1:-2]
#             subscribe = bool(message[5][1:-2])
#             if username in users.keys():
#                 if youtuber in subscriptions:
#                     if subscribe:
#                         if username not in subscriptions[youtuber]:
#                             subscriptions[youtuber].append(username)
#                             print(f'{username} subscribed to {youtuber} successfully...')
#                         else:
#                             print(f'[ERROR] : {username} is not subscribed to {youtuber}')
#                     else:
#                         if username not in subscriptions[youtuber]:
#                             print(f'[ERROR] : {username} is not subscribed to {youtuber}')
#                         else:
#                             subscriptions[youtuber].remove(username)
#                             print(f'{username} unsubscribed {youtuber} successfully...')
#                 else:
#                     print(f"[ERROR] : youtuber '{youtuber}' dosn't exist...")
#             else:
#                 print(f"[ERROR] : Username '{username}' not registered...")

#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue='user_requests')
#     channel.basic_consume(queue='user_requests', on_message_callback=callback, auto_ack=True)

#     print('YouTube server is waiting for user requests...')
#     while running:
#         try:
#             channel.start_consuming()
#         except KeyboardInterrupt:
#             print("Stopping user requests consumer...")
#             break
#     connection.close()


# def consume_youtuber_requests():
#     def callback(ch, method, properties, body):

#         global running
#         message = body.decode()

#         if message.lower() == 'stop':
#             running = False
#             return
#         # _______________________________________
#         if len(message.split()) == 1:
#             name = message
#             if name in subscriptions:
#                 print(f'[FAIL] : chanel whith name "{name}" already exists')
#             else:
#                 subscriptions[name] = []
#                 print(f'[SUCCESS] : registered the chanel name "{name}"')
#         else :
#             notify_users(body.decode())

#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue='youtuber_requests')
#     channel.basic_consume(queue='youtuber_requests', on_message_callback=callback, auto_ack=True)

#     print('YouTube server is waiting for YouTuber requests...')

#     while running:
#         try:
#             channel.start_consuming()
#         except KeyboardInterrupt:
#             print("Stopping youtuber requests consumer...")
#             break

#     connection.close()


# def notify_users(video_message):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()
#     print(subscriptions)
#     channel.queue_declare(queue='user_notifications')
#     channel.basic_publish(exchange='', routing_key='user_notifications', body=video_message)
#     print(f"sending: {video_message}")
#     print("Notification sent to all users")
#     connection.close()


# if __name__ == '__main__':
#     user_thread = threading.Thread(target=consume_user_requests)
#     youtuber_thread = threading.Thread(target=consume_youtuber_requests)

#     user_thread.start()
#     youtuber_thread.start()

#     try:
#         user_thread.join()
#         youtuber_thread.join()
#     except KeyboardInterrupt:
#         running = False

import pika
import threading

subscriptions = {}
users = {}
running = True

def consume_user_requests():
    def callback(ch, method, properties, body):
        global running
        message = body.decode()
        if message.lower() == 'stop':
            running = False
            return
        message = message.split()
        username = message[1][1:-2]
  
        if len(message) == 4:
            if message[3]:
                if username in users:
                    print(f"[ERROR] : username '{username}' already exists, unable to register the user")
                else:
                    users[username] =[]
                    print(f"[SUCCESS] : Registered username '{username}'...")
        elif len(message) == 6:
            youtuber = message[3][1:-2]
            temp = message[5][1:-2]
            if temp == "True":
                subscribe = True
            elif temp == "False":
                subscribe = False
          
            if username in users.keys():  
                if youtuber in subscriptions.keys():
                    if subscribe:
                        if username not in subscriptions[youtuber]:
                            subscriptions[youtuber].append(username)
                            print(f'{username} subscribed to {youtuber} successfully...')
                        else:
                            print(f'[ERROR] : {username} is already subscribed to {youtuber}')
                    else:
                        
                        if username not in subscriptions[youtuber]:
                            print(f'[ERROR] : {username} is not subscribed to {youtuber}')
                        else:
                            subscriptions[youtuber].remove(username)
                            print(f'{username} unsubscribed {youtuber} successfully...')
                else:
                    print(f"[ERROR] : youtuber '{youtuber}' dosn't exist...")
            else:
                print(f"[ERROR] : Username '{username}' not registered...")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='user_requests')
    consumer_tag = channel.basic_consume(queue='user_requests', on_message_callback=callback, auto_ack=True)

    print('YouTube server is waiting for user requests...')
    while running:
        try:
            channel.connection.process_data_events()
        except KeyboardInterrupt:
            print("Stopping user requests consumer...")
            channel.basic_cancel(consumer_tag)
            break
    connection.close()

def consume_youtuber_requests():
    def callback(ch, method, properties, body):
        global running
        message = body.decode()
        if message.lower() == 'stop':
            running = False
            return
        message = message.split()
        if len(message) == 1:
            name = message[0]
            if name in subscriptions:
                print(f'[FAIL] : channel with name "{name}" already exists')
            else:
                subscriptions[name] = []
                print(f'[SUCCESS] : registered the channel name "{name}"')
        else:
            notify_users(message[0],body.decode())

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='youtuber_requests')
    consumer_tag = channel.basic_consume(queue='youtuber_requests', on_message_callback=callback, auto_ack=True)

    print('YouTube server is waiting for YouTuber requests...')
    while running:
        try:
            channel.connection.process_data_events()
        except KeyboardInterrupt:
            print("Stopping youtuber requests consumer...")
            channel.basic_cancel(consumer_tag)
            break
    connection.close()

def notify_users(youtuber,video_message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    for user in subscriptions[youtuber]:
        channel.queue_declare(queue=user)
        channel.basic_publish(exchange='', routing_key=user, body=video_message)
    print(f"sending: {video_message}")
    print("Notification sent to all users")
    connection.close()

if __name__ == '__main__':
    user_thread = threading.Thread(target=consume_user_requests)
    youtuber_thread = threading.Thread(target=consume_youtuber_requests)

    user_thread.start()
    youtuber_thread.start()

    try:
        user_thread.join()
        youtuber_thread.join()
    except KeyboardInterrupt:
        running = False
