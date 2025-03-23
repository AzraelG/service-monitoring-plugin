from src.services.base_service import BaseService


class LogstashService(BaseService):

    def get_status(self):
        print("logstash")
