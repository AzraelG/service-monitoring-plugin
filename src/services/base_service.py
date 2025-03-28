"""
Base Service Class for handling service interaction.

This module defines a `BaseService` class that provides a base for interacting 
with different services. It manages service credentials (username and password) 
and provides a `get_status` method, which must be implemented by subclasses.

The class also includes a `get_service` method that returns the appropriate 
service class based on a given service name (without instantiating it).

Modules:
    logging
    src.lib.logging_config
    src.lib.http_driver.HttpDriver
    src.lib.exceptions.ServiceNotFoundError

Example Usage:
    service = BaseService.get_service("exampleService")
    service_instance = service(base_endpoint, user, password)
"""

import logging
from src.lib.http_driver import HttpDriver
from src.lib.exceptions import ServiceNotFoundError


class BaseService():
    """
    A base class for managing services and interacting with service APIs.

    The `BaseService` class provides a common interface for interacting with 
    different services. It holds common attributes like the base endpoint, user 
    credentials (username and password), and the HTTP driver to interact with 
    service APIs.

    The class defines a method `get_status` which must be implemented by 
    subclasses to fetch the status of the service.

    Attributes:
        log (logging.Logger): Logger instance for debugging and error logging.
        driver (HttpDriver): The HTTP driver used to interact with service APIs.
        base_endpoint (str): The base URL of the service API endpoint.
        user (str): The username used for authentication.
        password (str): The password used for authentication.
    """

    def __init__(self, base_endpoint, user, password, driver=HttpDriver):
        """
        Initializes the BaseService with credentials and endpoint information.

        Args:
            base_endpoint (str): The base URL of the service API endpoint.
            user (str): The username for authentication.
            password (str): The password for authentication.
            driver (HttpDriver): The HTTP driver used to interact with the service, 
                defaults to `HttpDriver`.

        This method sets up the logging, driver instance, and service credentials.
        """
        self.log = logging.getLogger(__name__)
        self.driver = driver()
        self.base_endpoint = base_endpoint
        self.user = user
        self.password = password

    def get_status(self):
        """
        Placeholder method that must be implemented by subclasses to retrieve 
        the status of the service.

        This method should be overridden by any subclass of `BaseService` to 
        fetch and return the status of the respective service.

        Raises:
            NotImplementedError: Subclasses must implement the `get_status` method.
        """
        raise NotImplementedError(
            "Subclasses must implement the get_status() method")

    @classmethod
    def get_service(cls, service_name):
        """
        Returns the appropriate service class based on the provided service name.

        This method looks up the service class by name (in lowercase), searching 
        through the subclasses of `BaseService`. If the service is not found, 
        it raises a `ServiceNotFoundError`.

        Args:
            service_name (str): The name of the service (e.g., "exampleService").

        Returns:
            class: The corresponding service class (but not instantiated).

        Raises:
            ServiceNotFoundError: If the service name is not recognized or not found 
                among the subclasses.
        """
        services = {sub.__name__.replace(
            "Service", "").lower(): sub for sub in cls.__subclasses__()}

        try:
            return services[service_name.lower()]
        except KeyError as e:
            raise ServiceNotFoundError(
                f"ERROR: Service '{service_name}' not recognized!") from e
