from src.connection.sql_connection import SQLConnection
import pytest


@pytest.fixture
def sample_sql_connection():
    return SQLConnection(
        host="localhost",
        port=1433,
        user="Abazar",
        password="12345",
        database="Fishes",
    )


# region Initialization test (__init__)

class TestSqlConnectionInit():
    def test_attributes_set_correctly(self, sample_sql_connection):
        assert sample_sql_connection.host == "localhost"
        assert sample_sql_connection.user == "Abazar"
        assert sample_sql_connection.password == "12345"
        assert sample_sql_connection.database == "Fishes"
        assert sample_sql_connection.port == 1433

    def test_engine_start_empty(self, sample_sql_connection):
        assert sample_sql_connection.engine is None

    def test_init_does_not_return(self):
        s = SQLConnection(host="localhost", port=1433, user="Abazar", password="12345", database="Fishes")
        assert s is not None


# endregion


# region Connect test

from unittest.mock import patch, MagicMock


class TestConnection:
    def test_connect_creates_engine_windows_auth(self, sample_sql_connection):
        with patch("src.connection.sql_connection.sqlalchemy.create_engine") as mock_create:
            sample_sql_connection.connect()
            assert sample_sql_connection.engine is not None
            mock_create.assert_called_once()

    def test_connect_windows_auth_connection_string(self):
        conn = SQLConnection(host="myhost", port=1433, database="MyDB", windows_authentication=True)
        with patch("src.connection.sql_connection.sqlalchemy.create_engine") as mock_create:
            conn.connect()
            call_args = mock_create.call_args[0][0]
            assert call_args == "mssql+pymssql://myhost:1433/MyDB"

    def test_connect_sql_auth_connection_string(self):
        conn = SQLConnection(
            host="myhost", port=1433, user="sa",
            password="pass123", database="MyDB",
            windows_authentication=False
        )
        with patch("src.connection.sql_connection.sqlalchemy.create_engine") as mock_create:
            conn.connect()
            call_args = mock_create.call_args[0][0]
            expected = f"mssql+pymssql://{conn.user}:{conn.password}@{conn.host}:{conn.port}/{conn.database}"
            assert call_args == expected

# endregion
