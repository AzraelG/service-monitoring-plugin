import nagiosplugin
from src.services.base_service import BaseService
from services.elasticsearch_service import ElasticsearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService
from src.nagios.service_health_resource import ServiceHealthResource
from src.nagios.service_health_context import ServiceHealthContext
from src.lib.exceptions import ServiceRequestError


service_name = "elasticsearch"
user = "pippo"
password = "secret"
base_endpoint = "https://putoelquelee"

if __name__ == "__main__":

    service_class = BaseService.get_service(service_name)
    service = service_class(user=user, password=password,
                            base_endpoint=base_endpoint)
    custom_description = None
    try:
        # service_status = service.get_status()
        service_status = "OK"

    except ServiceRequestError as e:
        service_status = "UNKNOWN"
        custom_description = "Connection Error"

    check = nagiosplugin.Check(
        ServiceHealthResource(
            service_status),
        ServiceHealthContext('service_health',
                             custom_description)
    )
    check.name = ''
    check.main()
