from src.services.base_service import BaseService


class LogstashService(BaseService):

    def check(self):
        print("logstash")
