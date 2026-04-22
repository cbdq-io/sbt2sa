@system
Feature: End to End Tests

    Place messages onto a topic and ensure they're loaded onto
    blob storage.

Scenario: Entry Criteria
    Given the Azurite Blob Connection String
    And the Service Bus Emulator Connection String
    When the Azurite Blob Service Client is Created
    Then create the container
    And produce the messages to the topic
    And run the function

Scenario: Exit Criteria
    Given the Azurite Blob Connection String
    And the TestInfra host with URL "local://" is ready
    When the Azurite Blob Service Client is Created
    And the TestInfra command is "docker compose logs sut && curl localhost:8000/metrics"
    Then the blob count should be 2
    And the earliest file should contain 500 messages
    And the latest file should contain 13 messages
    And the TestInfra command stdout contains "There are dead-letter messages on mytopic/test2"
    And the TestInfra command stdout contains "widget_message_count_total "
