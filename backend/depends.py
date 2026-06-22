from backend.database.postgres import BasePostgresConnection
from backend.service.base_service import BaseService
from backend.repository.postgres_repo import BasePostgresRepo

base_connection = BasePostgresConnection(user="myuser", password="mypassword", host="localhost", database="mydatabase")
base_service = BaseService(postgres_repo=BasePostgresRepo())
def get_base_servie() -> BaseService:
    return base_service

