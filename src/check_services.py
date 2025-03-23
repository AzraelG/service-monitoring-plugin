import nagiosplugin
from src.services.base_service import BaseService
from src.services.elastic_search_service import ElasticSearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService
from src.nagios.service_health_resource import ServiceHealthResource
from src.nagios.service_health_context import ServiceHealthContext


service_name = "elasticsearch"
user = "pippo"
password = "secret"
base_endpoint = "https://putoelquelee"

if __name__ == "__main__":
    service_class = BaseService.get_service(service_name)
    service = service_class(user, password, base_endpoint)

   # service.get_status()
    service_status = "Critical"
    check = nagiosplugin.Check(
        ServiceHealthResource(
            service_status=service_status),
        ServiceHealthContext('service_health')
    )
    check.name = ''
    check.main()
