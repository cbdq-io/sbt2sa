Feature: Test the Container
    Scenario Outline: Present Files Owner By the App User
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra file is <path>
        Then the TestInfra file is present
        And the TestInfra file type is file
        And the TestInfra file owner is appuser
        And the TestInfra file group is appuser

        Examples:
            | path                                      |
            | /usr/local/bin/multi-topic-entrypoint.py  |
            | /usr/local/bin/nukedlq.py                 |

    Scenario Outline: Python Packages
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra pip package is <pip_package>
        Then the TestInfra pip package is present

        Examples:
            | pip_package       |
            | azure-servicebus  |
            | prometheus-client |
            | smart_open        |
