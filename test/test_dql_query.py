from sql.query.dql.dql_query import DQLQuery
import pytest


@pytest.fixture
def sample_dql_query():
    return DQLQuery(
        database="database_one",
        schema="schema_one",
        table="table_one"
    )


# region Initialization test (__init__)
class TestDQLQueryInit:
    def test_attributes_set_correctly(self, sample_dql_query):
        assert sample_dql_query.database == "database_one"
        assert sample_dql_query.schema == "schema_one"
        assert sample_dql_query.table == "table_one"

    def test_query_starts_empty(self, sample_dql_query):
        assert sample_dql_query.query == ""

    def test_init_does_not_return(self):
        q = DQLQuery("db", "sch", "tbl")
        assert q.__init__("db", "sch", "tbl") is None


# endregion


# region Select test

class TestSelect:
    def test_select_with_columns(self, sample_dql_query):
        sample_dql_query.select(["col1", "col2", "col3"])
        assert sample_dql_query.query == "SELECT col1, col2, col3 FROM database_one.schema_one.table_one"

    def test_select_without_columns_returns_star(self, sample_dql_query):
        sample_dql_query.select(None)
        assert sample_dql_query.query == "SELECT * FROM database_one.schema_one.table_one"

    def test_select_with_empty_list(self, sample_dql_query):
        # [] is also falsy so it behaves like None
        sample_dql_query.select([])
        assert sample_dql_query.query == "SELECT * FROM database_one.schema_one.table_one"

    def test_select_with_single_column(self, sample_dql_query):
        sample_dql_query.select(["only_col"])
        assert sample_dql_query.query == "SELECT only_col FROM database_one.schema_one.table_one"

    def test_select_returns_none(self, sample_dql_query):
        assert sample_dql_query.select(["col1"]) is None


# endregion


# region Join test (all join types)

class TestJoin:
    @pytest.fixture
    def query_with_select(self, sample_dql_query):
        """We select first because join depends on self.query"""
        sample_dql_query.select(["id", "name"])
        return sample_dql_query

    @pytest.mark.parametrize("join_type,expected_keyword", [
        ("left", "LEFT JOIN"),
        ("right", "RIGHT JOIN"),
        ("inner", "INNER JOIN"),
        ("full", "FULL JOIN"),
        ("other", "FULL JOIN"),  # Anything other than left/right/inner → else means FULL
        ("", "FULL JOIN"),  # Empty string too → FULL
    ])
    def test_join_types(self, query_with_select, join_type, expected_keyword):
        result = query_with_select.join(
            schema="schema_two",
            table="table_two",
            first_column="id",
            second_column="user_id",
            join_type=join_type,
        )
        sql = str(result)
        assert expected_keyword in sql
        assert "schema_two.table_two" in sql
        assert "ON" in sql
        assert "id" in sql and "user_id" in sql

    def test_join_does_not_update_self_query(self, query_with_select):
        original_query = query_with_select.query
        query_with_select.join("s2", "t2", "id", "id", "inner")
        assert query_with_select.query == original_query

    def test_left_join_sql_content(self, query_with_select):
        result = query_with_select.join("schema_two", "table_two", "id", "user_id", "left")
        sql = str(result)
        # We check the overall structure
        assert "SELECT id, name FROM database_one.schema_one.table_one" in sql
        assert "LEFT JOIN schema_two.table_two" in sql
        assert "schema_one.table_one.id" in sql


# endregion

# region Where test

class TestWhere:
    def test_where_adds_condition(self, sample_dql_query):
        sample_dql_query.select(["*"])
        sample_dql_query.where("age > 18")
        sql = str(sample_dql_query.query)
        assert "WHERE" in sql
        assert "age > 18" in sql

    def test_where_returns_none(self, sample_dql_query):
        sample_dql_query.select(["*"])
        assert sample_dql_query.where("age > 18") is None

    def test_where_with_string_condition(self, sample_dql_query):
        sample_dql_query.select(["name", "age"])
        sample_dql_query.where("name = 'Ali'")
        sql = str(sample_dql_query.query)
        assert "name = 'Ali'" in sql


# endregion

# region Group by test

class TestGroupBy:
    def test_group_by_contains_column(self, sample_dql_query):
        sample_dql_query.select(["department", "COUNT(*)"])
        result = sample_dql_query.group_by("department")
        sql = str(result)
        assert "GROUP BY" in sql
        assert "department" in sql

    def test_group_by_does_not_update_self_query(self, sample_dql_query):
        sample_dql_query.select(["department"])
        original = sample_dql_query.query
        sample_dql_query.group_by("department")
        assert sample_dql_query.query == original


# endregion

# region Having by test

class TestHaving:
    def test_having_contains_condition(self, sample_dql_query):
        sample_dql_query.select(["department", "COUNT(*)"])
        sample_dql_query.group_by("department")
        result = sample_dql_query.having("COUNT(*) > 5")
        sql = str(result)
        assert "HAVING" in sql
        assert "COUNT(*) > 5" in sql


# endregion

# region Order by test
class TestOrderBy:
    def test_order_by_contains_column(self, sample_dql_query):
        sample_dql_query.select(["name", "age"])
        result = sample_dql_query.order_by("age DESC")
        sql = str(result)
        assert "ORDER BY" in sql
        assert "age DESC" in sql


# endregion

# region Limit by test

class TestLimit:
    def test_limit_updates_query(self, sample_dql_query):
        sample_dql_query.select(["*"])
        sample_dql_query.limit(10)
        sql = str(sample_dql_query.query)
        assert "LIMIT 10" in sql

    def test_limit_returns_none(self, sample_dql_query):
        sample_dql_query.select(["*"])
        assert sample_dql_query.limit(5) is None

    def test_limit_with_zero(self, sample_dql_query):
        sample_dql_query.select(["*"])
        sample_dql_query.limit(0)
        sql = str(sample_dql_query.query)
        assert "LIMIT 0" in sql


# endregion

# region Build test

class TestBuild:

    def test_build_returns_current_query(self, sample_dql_query):
        sample_dql_query.select(["id", "name"])
        result = sample_dql_query.build()
        sql = str(result)
        assert "SELECT id, name FROM database_one.schema_one.table_one" in sql

    def test_build_empty_query(self, sample_dql_query):
        result = sample_dql_query.build()
        assert str(result) == ""


# endregion

# region Condition helpers test

class TestComparisonConditions:
    @pytest.mark.parametrize("method,column,value,expected", [
        ("equal", "age", "18", "age = 18"),
        ("not_equal", "age", "18", "age <> 18"),
        ("greater_than", "age", "18", "age > 18"),
        ("less_than", "age", "18", "age < 18"),
        ("greater_than_equal", "age", "18", "age >= 18"),
        ("less_than_equal", "age", "18", "age <= 18"),
    ])
    def test_comparison_operators(self, sample_dql_query, method, column, value, expected):
        func = getattr(sample_dql_query, method)
        result = func(column, value)
        assert str(result) == expected


# endregion

# region Condition helpers(null) test

class TestNullConditions:
    @pytest.mark.parametrize("method,column,expected", [
        ("not_null", "email", "email NOT NULL"),
        ("is_null", "email", "email IS NULL"),
    ])
    def test_null_conditions(self, sample_dql_query, method, column, expected):
        func = getattr(sample_dql_query, method)
        result = func(column)
        assert str(result) == expected


# endregion

# region Integration test

class TestIntegration:
    def test_select_then_where(self, sample_dql_query):
        sample_dql_query.select(["name", "age"])
        sample_dql_query.where("age > 18")
        sql = str(sample_dql_query.query)
        assert "SELECT name, age FROM database_one.schema_one.table_one" in sql
        assert "WHERE age > 18" in sql

    def test_select_then_where_then_limit(self, sample_dql_query):
        sample_dql_query.select(["*"])
        sample_dql_query.where("age > 18")
        sample_dql_query.limit(10)
        sql = str(sample_dql_query.query)
        assert "SELECT * FROM database_one.schema_one.table_one" in sql
        assert "WHERE age > 18" in sql
        assert "LIMIT 10" in sql

    def test_full_query_with_all_helpers(self, sample_dql_query):
        sample_dql_query.select(["name", "age"])
        sample_dql_query.where("age > 18")
        sql = str(sample_dql_query.query)
        assert "SELECT name, age" in sql
        assert "WHERE age > 18" in sql

    def test_condition_helper_with_where(self, sample_dql_query):
        sample_dql_query.select(["*"])
        condition = str(sample_dql_query.greater_than("age", "18"))
        sample_dql_query.where(condition)
        sql = str(sample_dql_query.query)
        assert "age > 18" in sql
# endregion
