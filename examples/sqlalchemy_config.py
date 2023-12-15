from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from src.config.get_config import get_database_access


def get_sqlalchemy_engine():

    context = get_database_access()
    url = URL.create(
        drivername="postgresql",
        username=context['user'],
        password=context['password'],
        host=context['host'],
        port=context['port'],
        database=context['database']
    )
    print(url)
    return create_engine(url)
