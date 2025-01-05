from typing import Dict, Any, List
import psycopg
from psycopg_pool import ConnectionPool

class PostgreSQLBackend:
    """
    PostgreSQLBackend is a backend class for interacting with a PostgreSQL database
    using a connection pool. It provides methods for handling transactions, fetching,
    updating, inserting, and deleting data related to pages in the database.

    Attributes:
        _pool (ConnectionPool): Connection pool used to manage database connections.
        _transaction_conn (Optional[psycopg.Connection]): The current active connection during a transaction.
        _transaction_cur (Optional[psycopg.Cursor]): The current active cursor during a transaction.
        _in_transaction (bool): Flag indicating whether a transaction is in progress.
    """

    def __init__(self, pool: ConnectionPool):
        """
        Initializes the PostgreSQLBackend with necessary configurations.

        Args:
            pool (ConnectionPool): A psycopg2 connection pool to manage database connections.
        """
        self._pool = pool
        self._transaction_conn = None  # Holds the connection during a transaction
        self._transaction_cur = None  # Holds the cursor during a transaction
        self._in_transaction = False  # Flag to track transaction state

    def begin_transaction(self) -> None:
        """
        Begins a transaction by setting up a dedicated connection and cursor
        that will be used for all subsequent database operations.

        Raises:
            RuntimeError: If a transaction is already in progress.
        """
        if self._in_transaction:
            raise RuntimeError("A transaction is already in progress.")

        self._transaction_conn = self._pool.getconn()
        self._transaction_cur = self._transaction_conn.cursor()  # Create cursor here
        self._in_transaction = True

    def end_transaction(self, commit: bool = True) -> None:
        """
        Ends the transaction by either committing or rolling back all changes.

        Args:
            commit (bool): Flag to indicate whether to commit the transaction. Defaults to True.

        Raises:
            RuntimeError: If no active transaction is in progress.
        """
        if not self._in_transaction:
            raise RuntimeError("No active transaction to end.")

        try:
            if commit:
                self._transaction_conn.commit()
            else:
                self._transaction_conn.rollback()
        finally:
            # Clean up the transaction state
            self._transaction_cur.close()  # Close the cursor first
            self._pool.putconn(self._transaction_conn)  # Release the connection
            self._transaction_conn = None
            self._transaction_cur = None  # Reset the cursor
            self._in_transaction = False

    def in_transaction(self) -> bool:
        """
        Checks if a transaction is currently in progress.

        Returns:
            bool: True if a transaction is active, False otherwise.
        """
        return self._in_transaction

    def _get_connection(self) -> psycopg.Connection:
        """
        Returns the current connection to be used for operations.
        If a transaction is active, it returns the transaction connection.

        Returns:
            psycopg.Connection: The current database connection.
        """
        if self._in_transaction:
            return self._transaction_conn
        else:
            return self._pool.getconn()

    def _get_cursor(self, connection) -> psycopg.Cursor | psycopg.ServerCursor:
        """
        Returns the current cursor to be used for operations.
        If a transaction is active, it returns the transaction cursor.

        Args:
            connection (psycopg.Connection): The database connection to use for the cursor.

        Returns:
            psycopg.Cursor: The current database cursor.
        """
        if self._in_transaction:
            return self._transaction_cur
        else:
            return connection.cursor()

    def search(self, search_term: str, page: int, items_per_page: int, adult: bool) -> List[Dict[str, Any]]:
        """
        Searches the database for pages matching the search term with pagination.

        Args:
            search_term (str): The search term for querying the database.
            page (int): The page number for pagination.
            items_per_page (int): The number of results per page.
            adult (bool): Adult content filtering

        Returns:
            List[Dict[str, Any]]: A list of matching search results with scores.
        """
        offset = (page - 1) * items_per_page
        adult_formating = "" if adult else "(LOWER(metadata->>'rating')!='rta-5042-1996-1400-1577-rta' AND LOWER(metadata->>'rating')!='adult') AND"

        query = f"""
        SELECT 
            p.url_id, 
            u.url, 
            p.title, 
            0.7 * paradedb.score(p.url_id) + 0.3 * pr.rank AS score,
            paradedb.score(p.url_id) AS pdb_score,
            pr.rank
        FROM 
            pages p
        JOIN 
            urls u ON u.id = p.url_id
        JOIN 
            page_rank pr ON pr.url_id = p.url_id
        WHERE {adult_formating} (p.title @@@ %s OR p.description @@@ %s OR p.content @@@ %s)
        ORDER BY score DESC
        LIMIT %s OFFSET %s;
        """

        connection = self._get_connection()
        cursor = self._get_cursor(connection)
        cursor.execute(query, (search_term, search_term, search_term, items_per_page, offset))
        results = cursor.fetchall()

        if not self._in_transaction:
            connection.commit()
            cursor.close()
            self._pool.putconn(connection)

        return results






