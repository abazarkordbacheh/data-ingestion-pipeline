import sqlalchemy


class DQLQuery:
    """
    Creating a DQL query in SQL Server
    """

    def __init__(self, database: str, schema: str, table: str):
        """
        initialization
        :param database: Database name
        :param schema: Schema name
        :param table: Table name
        :returns: None
        """
        self.database = database
        self.schema = schema
        self.table = table
        self.query = ""

    def select(self, columns: list[str] | None) -> None:
        """
        Select columns
        :param columns: The list of column names
        :return: None
        """
        cols = ", ".join(columns) if columns else "*"
        self.query = (
            f"SELECT {cols} FROM {self.database}.{self.schema}.{self.table}"
        )

    def join(self, schema, table, first_column: str, second_column: str, join_type: str) -> None:
        """
        Join tables (INNER/LEFT/RIGHT/FULL)
        :param schema: Schema name
        :param table: Table name
        :param first_column: column name in First table
        :param second_column: column name in Second table
        :param join_type: Type of join (INNER/LEFT/RIGHT/FULL)
        :return: None
        """

        # left join
        if join_type == "left":
            return sqlalchemy.text(
                f"""{self.query}
                LEFT JOIN {schema}.{table}
                ON {self.schema}.{self.table}.{first_column} = {schema}.{table}.{second_column}"""
            )

        # right join
        elif join_type == "right":
            return sqlalchemy.text(
                f"""{self.query}
                RIGHT JOIN {schema}.{table}
                ON {self.schema}.{self.table}.{first_column} = {schema}.{table}.{second_column}"""
            )

        # inner join
        elif join_type == "inner":
            return sqlalchemy.text(
                f"""{self.query}
                INNER JOIN {schema}.{table}
                ON {self.schema}.{self.table}.{first_column} = {schema}.{table}.{second_column}"""
            )

        # full join
        else:
            return sqlalchemy.text(
                f"""{self.query}
                    FULL JOIN {schema}.{table}
                    ON {self.schema}.{self.table}.{first_column} = {schema}.{table}.{second_column}"""
            )

    def where(self, condition: str) -> None:
        """
        Filter rows (before grouping)
        :param condition: Condition
        :returns: None
        """
        self.query = sqlalchemy.text(
            f"""{self.query} 
            WHERE {condition}"""
        )

    def group_by(self, column: str) -> None:
        """
        Group by
        :param column: Column name
        :return: None
        """
        return sqlalchemy.text(
            f"""{self.query}
            GROUP BY {column}"""
        )

    def having(self, condition: str) -> None:
        """
        Having
        :param condition:
        :return: None
        """
        return sqlalchemy.text(
            f"""{self.query}
            HAVING {condition}"""
        )

    def order_by(self, column: str) -> None:
        """
        Order by
        :param column: Column name
        :return: None
        """
        return sqlalchemy.text(
            f"""{self.query}
            ORDER BY {column}"""
        )

    def limit(self, limit: int) -> None:
        """
        Limit
        :param limit: Count of rows
        :return: None
        """
        self.query = sqlalchemy.text(
            f"""{self.query} LIMIT {limit}"""
        )

    def build(self) -> sqlalchemy.text:
        """
        Build query
        :return: sqlalchemy.text
        """
        return sqlalchemy.text(self.query)

    # ---------------------- condition helpers ----------------------

    def equal(self, column: str, value: str) -> str:
        """
        Equal condition
        :param column: Column name
        :param value: Column value
        :return: Equal condition string
        """
        return sqlalchemy.text(
            f"""{column} = {value}"""
        )

    def not_equal(self, column: str, value: str) -> str:
        """
        Not equal condition
        :param column: Column name
        :param value: Column value
        :return: Not equal condition string
        """
        return sqlalchemy.text(
            f"""{column} <> {value}"""
        )

    def greater_than(self, column: str, value: str) -> str:
        """
        Greater than condition
        :param column: Column name
        :param value: Column value
        :return: Greater than condition string
        """
        return sqlalchemy.text(
            f"""{column} > {value}"""
        )

    def less_than(self, column: str, value: str) -> str:
        """
        Less than condition
        :param column: Column name
        :param value: Column value
        :return:  Less than condition string
        """
        return sqlalchemy.text(
            f"""{column} < {value}"""
        )

    def greater_than_equal(self, column: str, value: str) -> str:
        """
        Greater than equal condition
        :param column: Column name
        :param value: Column value
        :return: Greater than equal condition string
        """
        return sqlalchemy.text(
            f"""{column} >= {value}"""
        )

    def less_than_equal(self, column: str, value: str) -> str:
        """
        Less than equal condition
        :param column: Column name
        :param value: Column value
        :return: Less than equal condition string
        """
        return sqlalchemy.text(
            f"""{column} <= {value}"""
        )

    def not_null(self, column: str) -> str:
        """
        Not null condition
        :param column: Column name
        :return: Not null condition string
        """
        return sqlalchemy.text(
            f"""{column} NOT NULL"""
        )

    def is_null(self, column: str) -> str:
        """
        Is null condition
        :param column: Column name
        :return: Is null condition string
        """
        return sqlalchemy.text(
            f"""{column} IS NULL"""
        )

    def between(self, column: str, min_value: str, max_value: str) -> str:
        """"
        Between condition
        :param column: Column name
        :param min_value: Minimum value
        :param max_value: Maximum value
        :return: Between condition string
        """
        return sqlalchemy.text(
            f"""{min_value}<={column}>= {max_value}"""
        )
