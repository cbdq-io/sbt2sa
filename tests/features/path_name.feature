@unit
Feature: Path Name
    Scenario Outline: Path Name
        Given the container name is <container_name>
        And the topics directory is <topics_dir>
        And the path format is <path_format>
        And the timestamp is <timestamp>
        And the topic name is <topic_name>
        And the offset is <offset>
        When the load URI is created
        Then the path is <uri>

        Examples:
            | container_name | topics_dir | path_format                              | timestamp        | topic_name | offset | uri                                                                                                            |
            | mycontainer    | topics     | year=YYYY/month=MM/day=dd/hour=HH/min=mm | 2025-02-24T15:56 | mytopic    | 42     | azure://mycontainer/topics/mytopic/year=2025/month=02/day=24/hour=15/min=56/mytopic+0000000000000000042.bin.gz |
