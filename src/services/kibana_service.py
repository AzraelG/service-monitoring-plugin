from src.services.base_service import BaseService


class KibanaService(BaseService):

    def check(self):
        print("kibana")
