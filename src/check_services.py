from src.services.base_service import BaseService
from src.services.elastic_search_service import ElasticSearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService


service_name = "logstash"
user = "pippo"
password = "secret"
base_endpoint = "https://putoelquelee"

if __name__ == "__main__":
    service_class = BaseService.get_service(service_name)
    service = service_class(user, password, base_endpoint)

    service.check()
