from src.connection.base import BaseConnection
import sqlalchemy
import pymssql


class SQLConnection(BaseConnection):
    """
    SQLAlchemy connection class
    """

    def __init__(
            self,
            host: str = 'localhost',
            port: int = 1433,
            user='root',
            password: str = '',
            database: str = 'master',
            windows_authentication: bool = True
    ) -> None:
        """
        initialization
        :param host: Server ip address
        :param port: Port number
        :param user: User name
        :param password: Password
        :param database: Database name
        :param windows_authentication: True or False
        :returns: None
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.windows_authentication = windows_authentication
        self.engine = None

    def connect(self) -> None:
        """
        Create engine
        :return: None
        """
        if self.windows_authentication:
            connection_string = f"mssql+pymssql://{self.host}:{self.port}/{self.database}"
            self.engine = sqlalchemy.create_engine(connection_string)
        else:
            connection_string = (
                f"mssql+pymssql://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
            self.engine = sqlalchemy.create_engine(connection_string)

    def disconnect(self) -> None:
        """
        Disconnect engine
        :return: None
        """
        self.engine.dispose()
