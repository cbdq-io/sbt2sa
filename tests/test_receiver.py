"""Regression tests for concurrent Service Bus receiver access."""
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest
from azure.servicebus.exceptions import ServiceBusError

from SBT2Blob import Extractor, SerializedReceiver


@pytest.mark.parametrize('operation', [
    'receive_messages', 'complete_message', 'renew_message_lock', 'close',
])
def test_receiver_operations_wait_for_renewal(operation):
    sdk_receiver = Mock()
    receiver = SerializedReceiver(sdk_receiver)
    renewing = threading.Event()
    release_renewal = threading.Event()
    waiting = threading.Event()
    lock = threading.Lock()

    class ObservedLock:
        def __enter__(self):
            if not lock.acquire(blocking=False):
                waiting.set()
                lock.acquire()

        def __exit__(self, *args):
            lock.release()

    receiver._lock = ObservedLock()

    def renew(message):
        if message == 'first':
            renewing.set()
            assert release_renewal.wait(5)

    sdk_receiver.renew_message_lock.side_effect = renew
    args = () if operation in ('receive_messages', 'close') else ('second',)
    with ThreadPoolExecutor(max_workers=2) as executor:
        renewal = executor.submit(receiver.renew_message_lock, 'first')
        try:
            assert renewing.wait(5)
            foreground = executor.submit(getattr(receiver, operation), *args)
            assert waiting.wait(5)
            assert sdk_receiver.method_calls == [
                ('renew_message_lock', ('first',), {}),
            ]
        finally:
            release_renewal.set()
        renewal.result(timeout=5)
        foreground.result(timeout=5)
    getattr(sdk_receiver, operation).assert_called_with(*args)


def test_receive_forwards_options_and_releases_lock_on_error():
    sdk_receiver = Mock()
    receiver = SerializedReceiver(sdk_receiver)
    sdk_receiver.receive_messages.side_effect = ServiceBusError('receive failed')
    with pytest.raises(ServiceBusError):
        receiver.receive_messages(max_message_count=10, max_wait_time=5)
    sdk_receiver.receive_messages.assert_called_once_with(max_message_count=10, max_wait_time=5)
    sdk_receiver.receive_messages.side_effect = None
    assert receiver.receive_messages() is sdk_receiver.receive_messages.return_value


def test_extractor_registers_serialized_receiver(monkeypatch):
    client_factory = Mock()
    renewer_factory = Mock()
    monkeypatch.setattr('SBT2Blob.ServiceBusClient', client_factory)
    monkeypatch.setattr('SBT2Blob.AutoLockRenewer', renewer_factory)
    sdk_receiver = client_factory.from_connection_string.return_value.get_subscription_receiver.return_value
    message = Mock()
    sdk_receiver.receive_messages.return_value = [message]
    extractor = Extractor('connection', 'topic', 'subscription', False)

    assert extractor.get_messages() == [message]
    renewer_factory.return_value.register.assert_called_once_with(
        extractor.receiver, message, max_lock_renewal_duration=120,
    )
    assert isinstance(extractor.receiver, SerializedReceiver)
    extractor.accept_messages([message])
    sdk_receiver.complete_message.assert_called_once_with(message)


def test_cleanup_continues_after_service_bus_error(monkeypatch):
    client_factory = Mock()
    renewer_factory = Mock()
    monkeypatch.setattr('SBT2Blob.ServiceBusClient', client_factory)
    monkeypatch.setattr('SBT2Blob.AutoLockRenewer', renewer_factory)
    extractor = Extractor('connection', 'topic', 'subscription', False)
    client = client_factory.from_connection_string.return_value
    receiver = client.get_subscription_receiver.return_value
    calls = Mock()
    calls.attach_mock(renewer_factory.return_value.close, 'renewer')
    calls.attach_mock(receiver.close, 'receiver')
    calls.attach_mock(client.close, 'client')
    receiver.close.side_effect = ServiceBusError('receiver failed')

    extractor.close()

    assert [call[0] for call in calls.mock_calls] == ['renewer', 'receiver', 'client']
