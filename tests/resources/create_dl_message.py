"""Create a dead-letter message."""
from azure.servicebus import ServiceBusClient, ServiceBusMessage

conn_params = [
    'Endpoint=sb://localhost',
    'SharedAccessKeyName=RootManageSharedAccessKey',
    'SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true'
]
conn_str = ';'.join(conn_params)
topic = 'mytopic'
subscription = 'test2'
dlq_message_created = False

while not dlq_message_created:
    try:
        print('Opening client....')
        with ServiceBusClient.from_connection_string(conn_str) as client:
            with client.get_topic_sender(topic_name=topic) as sender:
                message = ServiceBusMessage('Hello, DLQ!'.encode())
                print('Sending message...')
                sender.send_messages(message)

            with client.get_subscription_receiver(topic_name=topic, subscription_name=subscription) as receiver:
                msgs = receiver.receive_messages(max_message_count=1)

                for msg in msgs:
                    print(f'Got message {msg}')
                    receiver.dead_letter_message(msg, reason='Testing DLQ', error_description='Forced')
                    print('Message sent to dead-letter.')
                    dlq_message_created = True
    except Exception as ex:
        print(f'WARNING: {ex}')
