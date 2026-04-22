"""Path Name feature tests."""
import datetime

from pytest_bdd import given, parsers, scenario, then, when

from SBT2Blob import LoadURI


@scenario('path_name.feature', 'Path Name')
def test_path_name():
    """Path Name."""


@given(parsers.parse('the container name is {container_name}'), target_fixture='container_name')
def _(container_name: str):
    """the container name is <container_name>."""
    return container_name


@given(parsers.parse('the offset is {offset:d}'), target_fixture='offset')
def _(offset: int):
    """the offset is <offset>."""
    return offset


@given(parsers.parse('the path format is {path_format}'), target_fixture='path_format')
def _(path_format: str):
    """the path format is <path_format>."""
    return path_format


@given(parsers.parse('the timestamp is {timestamp}'), target_fixture='timestamp')
def _(timestamp: str):
    """the timestampe is <timestamp>."""
    return datetime.datetime.fromisoformat(timestamp)


@given(parsers.parse('the topic name is {topic_name}'), target_fixture='topic_name')
def _(topic_name: str):
    """the topic name is <topic_name>."""
    return topic_name


@given(parsers.parse('the topics directory is {topics_dir}'), target_fixture='topics_directory')
def _(topics_dir: str):
    """the topics directory is <topics_dir>."""
    return topics_dir


@when('the load URI is created', target_fixture='load_uri')
def _(container_name: str, topics_directory: str, topic_name: str, path_format: str):
    """the load URI is created."""
    return LoadURI(
        container_name,
        topics_directory,
        topic_name,
        path_format
    )


@then(parsers.parse('the path is {expected_uri}'))
def _(expected_uri: str, load_uri: LoadURI, timestamp: datetime.datetime, offset: int):
    """the path is <uri>."""
    actual_uri = load_uri.uri(offset, timestamp)
    assert actual_uri == expected_uri
