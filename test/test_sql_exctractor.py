import pytest
import pandas as pd
from unittest.mock import MagicMock, call
from src.extract.sql_extractor import extract, get_max_id
from src.connection.sql_connection import SQLConnection


# region Helpers

def _make_connection(fetchmany_side_effect=None, keys=None, fetchone_return=None):
    """
    Build a fully wired SQLConnection mock.

    extract() call chain:
        conn.engine.connect()                     -> conn_proxy
        conn_proxy.execution_options(...)         -> exec_opts  (context manager)
        exec_opts.__enter__()                     -> ctx
        ctx.execute(query)                        -> result
        result.keys()                             -> columns
        result.fetchmany(chunk_size)              -> rows

    get_max_id() call chain:
        conn.engine.connect()                     -> connect_cm  (context manager)
        connect_cm.__enter__()                    -> ctx
        ctx.execute(query).fetchone()[0]          -> scalar
    """
    conn = MagicMock(spec=SQLConnection)
    conn.engine = MagicMock()

    # --------------- extract chain ---------------
    conn_proxy = MagicMock()
    conn.engine.connect.return_value = conn_proxy

    exec_opts_cm = MagicMock()
    conn_proxy.execution_options.return_value = exec_opts_cm

    ctx = MagicMock()
    exec_opts_cm.__enter__.return_value = ctx
    exec_opts_cm.__exit__.return_value = False

    result = MagicMock()
    if keys is not None:
        result.keys.return_value = keys
    if fetchmany_side_effect is not None:
        result.fetchmany.side_effect = fetchmany_side_effect
    ctx.execute.return_value = result

    # --------------- get_max_id chain ---------------
    connect_cm = MagicMock()
    conn.engine.connect.return_value = connect_cm          # reused mock; both paths share it

    max_ctx = MagicMock()
    connect_cm.__enter__.return_value = max_ctx
    connect_cm.__exit__.return_value = False

    if fetchone_return is not None:
        max_ctx.execute.return_value.fetchone.return_value = fetchone_return

    return conn, conn_proxy, ctx, result, max_ctx

# endregion

# endregion extract

class TestExtract:

    def _make_extract_mock(self, keys, fetchmany_side_effect):
        conn = MagicMock(spec=SQLConnection)
        conn.engine = MagicMock()

        conn_proxy = MagicMock()
        conn.engine.connect.return_value = conn_proxy

        exec_opts_cm = MagicMock()
        conn_proxy.execution_options.return_value = exec_opts_cm

        ctx = MagicMock()
        exec_opts_cm.__enter__.return_value = ctx
        exec_opts_cm.__exit__.return_value = False

        result = MagicMock()
        result.keys.return_value = keys
        result.fetchmany.side_effect = fetchmany_side_effect
        ctx.execute.return_value = result

        return conn, conn_proxy, ctx, result

    # --------------- happy path ---------------

    def test_yields_dataframes(self):
        conn, _, _, result = self._make_extract_mock(
            keys=["id", "name", "age"],
            fetchmany_side_effect=[
                [(1, "Ali", 25), (2, "Sara", 30)],
                [(3, "Reza", 28)],
                [],
            ],
        )
        chunks = list(extract(conn, "SELECT * FROM users", chunk_size=2))

        assert len(chunks) == 2
        assert all(isinstance(c, pd.DataFrame) for c in chunks)
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 1
        assert list(chunks[0].columns) == ["id", "name", "age"]

    def test_empty_result_yields_nothing(self):
        conn, _, _, _ = self._make_extract_mock(
            keys=["id"],
            fetchmany_side_effect=[[]],
        )
        assert list(extract(conn, "SELECT id FROM t", chunk_size=10)) == []

    def test_single_chunk(self):
        conn, _, _, _ = self._make_extract_mock(
            keys=["id", "value"],
            fetchmany_side_effect=[[(1, 100), (2, 200), (3, 300)], []],
        )
        chunks = list(extract(conn, "SELECT * FROM t", chunk_size=5))
        assert len(chunks) == 1
        assert len(chunks[0]) == 3

    def test_column_order_preserved(self):
        conn, _, _, _ = self._make_extract_mock(
            keys=["col_a", "col_b", "col_c"],
            fetchmany_side_effect=[[(1, 2, 3)], []],
        )
        chunks = list(extract(conn, "SELECT * FROM t", chunk_size=10))
        assert list(chunks[0].columns) == ["col_a", "col_b", "col_c"]

    # --------------- generator behaviour ---------------

    def test_returns_generator(self):
        conn, _, _, _ = self._make_extract_mock(keys=["id"], fetchmany_side_effect=[[]])
        gen = extract(conn, "SELECT id FROM t", chunk_size=10)
        assert hasattr(gen, "__iter__") and hasattr(gen, "__next__")

    def test_lazy_evaluation(self):
        """Generator must not consume data until iterated."""
        conn, _, _, result = self._make_extract_mock(
            keys=["id"],
            fetchmany_side_effect=[[(1,)], []],
        )
        gen = extract(conn, "SELECT id FROM t", chunk_size=1)
        result.fetchmany.assert_not_called()
        next(gen)
        result.fetchmany.assert_called()

    # --------------- execution options ---------------

    def test_stream_results_option_set(self):
        conn, conn_proxy, _, _ = self._make_extract_mock(
            keys=["id"], fetchmany_side_effect=[[]]
        )
        list(extract(conn, "SELECT id FROM t", chunk_size=50))
        conn_proxy.execution_options.assert_called_once_with(
            stream_results=True, yield_per=50
        )

    def test_fetchmany_called_with_chunk_size(self):
        chunk_size = 7
        conn, _, _, result = self._make_extract_mock(
            keys=["id"],
            fetchmany_side_effect=[[(i,) for i in range(7)], []],
        )
        list(extract(conn, "SELECT id FROM t", chunk_size=chunk_size))
        for c in result.fetchmany.call_args_list:
            assert c == call(chunk_size)

    # --------------- multiple chunks integrity ---------------

    def test_all_chunks_have_same_columns(self):
        conn, _, _, _ = self._make_extract_mock(
            keys=["x", "y"],
            fetchmany_side_effect=[[(1, 2)], [(3, 4)], [(5, 6)], []],
        )
        for chunk in extract(conn, "SELECT x, y FROM t", chunk_size=1):
            assert list(chunk.columns) == ["x", "y"]

    def test_total_row_count_across_chunks(self):
        conn, _, _, _ = self._make_extract_mock(
            keys=["id"],
            fetchmany_side_effect=[[(i,) for i in range(5)], [(i,) for i in range(3)], []],
        )
        chunks = list(extract(conn, "SELECT id FROM t", chunk_size=5))
        total_rows = sum(len(c) for c in chunks)
        assert total_rows == 8

# endregion


#region  get_max_id

class TestGetMaxId:

    def _make_max_id_mock(self, fetchone_value):
        conn = MagicMock(spec=SQLConnection)
        conn.engine = MagicMock()

        connect_cm = MagicMock()
        conn.engine.connect.return_value = connect_cm

        ctx = MagicMock()
        connect_cm.__enter__.return_value = ctx
        connect_cm.__exit__.return_value = False

        ctx.execute.return_value.fetchone.return_value = fetchone_value
        return conn, ctx

    # --------------- happy path ---------------

    def test_returns_correct_integer(self):
        conn, _ = self._make_max_id_mock((42,))
        assert get_max_id(conn, "SELECT MAX(id) FROM t") == 42

    def test_returns_int_type(self):
        conn, _ = self._make_max_id_mock((7,))
        assert isinstance(get_max_id(conn, "SELECT MAX(id) FROM t"), int)

    def test_returns_zero_when_result_is_zero(self):
        conn, _ = self._make_max_id_mock((0,))
        assert get_max_id(conn, "SELECT MAX(id) FROM t") == 0

    def test_returns_large_id(self):
        conn, _ = self._make_max_id_mock((999_999_999,))
        assert get_max_id(conn, "SELECT MAX(id) FROM t") == 999_999_999

    def test_executes_query(self):
        conn, ctx = self._make_max_id_mock((1,))
        query = "SELECT MAX(id) FROM products"
        get_max_id(conn, query)
        ctx.execute.assert_called_once_with(query)

    # --------------- context manager usage ---------------

    def test_uses_context_manager(self):
        conn, _ = self._make_max_id_mock((1,))
        connect_cm = conn.engine.connect.return_value
        get_max_id(conn, "SELECT MAX(id) FROM t")
        connect_cm.__enter__.assert_called_once()
        connect_cm.__exit__.assert_called_once()

    # --------------- bug exposure ---------------

    def test_none_result_raises_type_error(self):
        """
        BUG: int(None) is called BEFORE the None-check, so an empty
        table raises TypeError instead of returning 0.

        Fix:
            result = connection.execute(query).fetchone()[0]
            return int(result) if result is not None else 0
        """
        conn, _ = self._make_max_id_mock((None,))
        with pytest.raises(TypeError):
            get_max_id(conn, "SELECT MAX(id) FROM empty_table")
# endregion