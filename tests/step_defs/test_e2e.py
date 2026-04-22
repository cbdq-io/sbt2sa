"""End to End Tests feature tests."""
import json
import logging
import os
import time

import azure.common
import azure.common.exceptions
import azure.core
import azure.core.exceptions
import azure.storage
import azure.storage.blob
import lorem
import smart_open
from azure.core.exceptions import ResourceExistsError
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.storage.blob import BlobServiceClient
from pytest_bdd import given, parsers, scenario, then, when

from SBT2Blob import main

CONTAINER_NAME = 'mycontainer'
MESSAGE_COUNT = 512
TOPIC_NAME = 'mytopic'

logging.basicConfig()
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)


@scenario('e2e.feature', 'Entry Criteria')
def test_entry_criteria():
    """Entry Criteria."""


@scenario('e2e.feature', 'Exit Criteria')
def test_exit_criteria():
    """Exit Criteria."""


@given('the Azurite Blob Connection String', target_fixture='STORAGE_ACCOUNT_CONNECTION_STRING')
def _():
    """the Azurite Blob Connection String."""
    response = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;'
    response += 'AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;'
    response += 'BlobEndpoint=http://localhost:10000/devstoreaccount1;'
    return response


@given('the Service Bus Emulator Connection String', target_fixture='SERVICE_BUS_EMULATOR_CONNECTION_STRING')
def _():
    """the Azurite Blob Connection String."""
    response = 'Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;'
    response += 'SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;'
    return response


@when('the Azurite Blob Service Client is Created', target_fixture='blob_client')
def _(STORAGE_ACCOUNT_CONNECTION_STRING: str):
    """the Azurite Blob Service Client is Created."""
    logger.debug(f'Creating a client with connection string "{STORAGE_ACCOUNT_CONNECTION_STRING}".')
    return azure.storage.blob.BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)


@then('create the container')
def _(blob_client: BlobServiceClient):
    """create the container."""
    try:
        logger.debug(f'Creating the container "{CONTAINER_NAME}"...')
        blob_client.create_container(CONTAINER_NAME)
        logger.info(f'Container "{CONTAINER_NAME}" successfully created.')
    except ResourceExistsError:
        logger.debug(f'Deleting existing container "{CONTAINER_NAME}"...')
        blob_client.delete_container(CONTAINER_NAME)
        logger.info(f'Container "{CONTAINER_NAME}" successfully deleted.')
        logger.debug(f'Recreating the container "{CONTAINER_NAME}"...')
        blob_client.create_container(CONTAINER_NAME)
        logger.info(f'Container "{CONTAINER_NAME}" successfully recreated.')
    except Exception as e:
        logger.error(e)
        raise Exception(e)


@then('create a dead-letter message')
def _(SERVICE_BUS_EMULATOR_CONNECTION_STRING: str):
    """create a dead-letter message."""
    topic = 'mytopic'
    subscription = 'test2'

    with ServiceBusClient.from_connection_string(SERVICE_BUS_EMULATOR_CONNECTION_STRING) as client:
        sender = client.get_topic_sender(topic)
        message = ServiceBusMessage('Hello, DLQ!'.encode())
        sender.send_messages(message)

        with client.get_subscription_receiver(topic, subscription, max_wait_time=5) as receiver:
            msgs = receiver.receive_messages(max_message_count=1)

            for msg in msgs:
                print(f'Received: {msg.body}')
                receiver.dead_letter_message(msg, reason='Testing DLQ', error_description='Forced')
                print('Moved to DLQ')


@then('produce the messages to the topic')
def _(SERVICE_BUS_EMULATOR_CONNECTION_STRING: str):
    """produce the messages to the topic."""
    logger.debug('Creating a Service Bus client...')
    client = ServiceBusClient.from_connection_string(SERVICE_BUS_EMULATOR_CONNECTION_STRING)
    logger.debug(f'Creating a sender for "{TOPIC_NAME}"...')
    sender = client.get_topic_sender(TOPIC_NAME)

    for idx, message in enumerate(range(MESSAGE_COUNT)):
        message = lorem.sentence()
        message_body = {
            'message_number': idx,
            'payload': message
        }
        message = ServiceBusMessage(body=json.dumps(message_body).encode())
        sender.send_messages(message)
        logger.debug(f'Sent message {idx}/{MESSAGE_COUNT}.')
        time.sleep(0.05)

    sender.close()
    client.close()


@then('run the function')
def _(STORAGE_ACCOUNT_CONNECTION_STRING: str, SERVICE_BUS_EMULATOR_CONNECTION_STRING: str):
    """run the function."""
    os.environ['CONTAINER_NAME'] = CONTAINER_NAME
    os.environ['PATH_FORMAT'] = 'year=YYYY/month=MM/day=dd/hour=HH'
    os.environ['STORAGE_ACCOUNT_CONNECTION_STRING'] = STORAGE_ACCOUNT_CONNECTION_STRING
    os.environ['SERVICE_BUS_CONNECTION_STRING'] = SERVICE_BUS_EMULATOR_CONNECTION_STRING
    os.environ['SUBSCRIPTION_NAME'] = 'test'
    os.environ['TOPIC_NAME'] = TOPIC_NAME
    os.environ['LOG_LEVEL'] = 'DEBUG'
    main()
    main()


@then('the blob count should be 2', target_fixture='blob_name_list')
def _(blob_client: azure.storage.blob.BlobServiceClient):
    """the blob count should be 2."""
    container_client = blob_client.get_container_client(container=CONTAINER_NAME)
    blob_name_list = []

    for blob_name in container_client.list_blob_names():
        if not blob_name.startswith('topics/'):
            logger.debug(f'Ignoring {blob_name} as part of the tests.')
            continue

        blob_name_list.append(blob_name)

    assert len(blob_name_list) == 2, blob_name_list
    return sorted(blob_name_list)


@then(parsers.parse('the {position} file should contain {expected_message_count:d} messages'))
def _(position: str, expected_message_count: int, blob_name_list: list, blob_client: BlobServiceClient):
    """the earliest file should contain 500 messages."""
    if position == 'earliest':
        blob_name = blob_name_list[0]
    else:
        blob_name = blob_name_list[1]

    transport_params = {
        'client': blob_client
    }
    uri = f'azure://mycontainer/{blob_name}'
    actual_record_count = 0

    with smart_open.open(uri, 'rb', transport_params=transport_params) as stream:
        for message in stream:
            actual_record_count += 1

    assert actual_record_count == expected_message_count, uri
