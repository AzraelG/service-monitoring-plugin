from src.services.base_service import BaseService


class ElasticSearchService(BaseService):

    def check(self):
        print("elastic")
