import pika
import sys

def register(youtuber):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='youtuber_requests')

    message = youtuber
    channel.basic_publish(exchange='', routing_key='youtuber_requests', body=message)

    print("SUCCESS")
    connection.close()



def publish_video(youtuber, video_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='youtuber_requests')

    message = f"{youtuber} uploaded {video_name}"
    channel.basic_publish(exchange='', routing_key='youtuber_requests', body=message)

    print("SUCCESS")
    connection.close()

if __name__ == '__main__':
    youtuber_name = sys.argv[1]
    video_name = ' '.join(sys.argv[2:])
    # youtuber_name = "nerix"
    # register(youtuber_name)
    publish_video(youtuber_name, video_name)
