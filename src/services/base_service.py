import logging
import src.lib.logging_config
from src.lib.http_driver import HttpDriver
from src.lib.exceptions import ServiceNotFoundError


class BaseService():
    def __init__(self, base_endpoint, user, password, driver=HttpDriver):
        self.log = logging.getLogger(__name__)
        self.driver = driver()
        self.base_endpoint = base_endpoint
        self.user = user
        self.password = password

    def get_status(self):
        """
        Each subclass must implement this method.
        """
        raise NotImplementedError(
            "Subclasses must implement the get_status() method")

    @classmethod
    def get_service(cls, service_name):
        """"
        Returns the appropriate class without instantiating it yet."
        """
        services = {sub.__name__.replace(
            "Service", "").lower(): sub for sub in cls.__subclasses__()}

        try:
            return services[service_name.lower()]
        except KeyError as e:
            raise ServiceNotFoundError(
                f"ERROR: Service '{service_name}' not recognized!") from e
