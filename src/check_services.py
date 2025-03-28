"""
This script provides a command-line tool to check the health status of various services 
(elasticsearch, kibana, logstash) and return a Nagios-compatible output.

It uses the Nagios plugin framework to report the status of the services based on their 
current health. The health check includes handling various errors, including connection 
errors, timeouts, authentication errors, HTTP status errors, and unexpected errors.

Usage:
    $ python check_service.py --check <service> 
                              --endpoint <endpoing> 
                              --user <username> 
                              --password <password>

Services supported:
    - elasticsearch
    - kibana
    - logstash
"""

import logging
import click
import nagiosplugin
from src.services.base_service import BaseService
from src.services.elasticsearch_service import ElasticsearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService
from src.nagios.service_health_resource import ServiceHealthResource
from src.nagios.service_health_context import ServiceHealthContext
from src.lib.exceptions import (
    HttpConnectionError,
    HttpTimeoutError,
    HttpAuthenticationError,
    HttpStatusError,
    HttpUnexpectedError,
)


log = logging.getLogger(__name__)


@click.command()
@click.option('--check', required=True, type=click.Choice(['elasticsearch', 'kibana', 'logstash']),
              help='Specify the service to check.')
@click.option('--endpoint', required=True, help='Service endpoint.')
@click.option('--user', required=True, help='Username for authentication.')
@click.option('--password', required=True, hide_input=True, help='Password for authentication.')
def check_service(check, endpoint, user, password):
    """
    Check the health status of a given service and return a Nagios-compatible output.
    """
    service_class = BaseService.get_service(check)
    service = service_class(
        user=user, password=password, base_endpoint=endpoint)
    custom_description = None

    try:
        service_status = service.get_status()

    except HttpConnectionError as e:
        log.error("Connection Error: %s", e)
        service_status = "UNKNOWN"
        custom_description = "Unable to connect to the service."

    except HttpTimeoutError as e:
        log.error("Timeout Error: %s", e)
        service_status = "UNKNOWN"
        custom_description = "Service request timed out."

    except HttpAuthenticationError as e:
        log.error("Authentication Error: %s", e)
        service_status = "UNKNOWN"
        custom_description = "Authentication failed for the service."

    except HttpStatusError as e:
        log.error("HTTP Status Error: %s", e)
        service_status = "UNKNOWN"
        custom_description = "An HTTP status error occurred."

    except HttpUnexpectedError as e:
        log.error("Unexpected Error: %s", e)
        service_status = "UNKNOWN"
        custom_description = "An unexpected error occurred."

    check = nagiosplugin.Check(
        ServiceHealthResource(service_status),
        ServiceHealthContext(custom_description=custom_description)
    )
    check.name = ''
    check.main()


if __name__ == "__main__":
    check_service()
