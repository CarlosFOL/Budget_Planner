import os
import psycopg2
from psycopg2.errors import CheckViolation, ProgrammingError, UniqueViolation
from widgets import Message_Box


class DB_conn:
    """
    It represents a database connection 
    """

    def __init__(self, dbname: str):
        self.dbname = dbname
        self._get_credentials()

    def _get_credentials(self):
        """
        Get the credentials to connect to the 
        budget planner database
        """
        self.user = os.getenv("PSQL_USER")
        self.passw = os.getenv("PSQL_PASS")
        self.host = os.getenv("PSQL_HOST")
        self.port = os.getenv("PSQL_PORT")

    def execute(self, query: str, params: tuple = None) -> list | None:
        """
        Execute SQL query with optional parameters. Returns results if any, 
        otherwise commits the transaction.
        """
        self.start()
        try:
            if type(query) == str:
                self.cursor.execute(query, params)
            else:
                for sql_cmd in query:            
                    self.cursor.execute(sql_cmd)
        except UniqueViolation:
            Message_Box(title="Transaction Error", 
                        text="You're trying to register a record that already exists.",
                        icon="Critical")
        except CheckViolation:
            Message_Box(title="Negative balance",
                        text="The transaction cannot be completed. You don't have enough money.",
                        icon="Critical")
        except Exception as e:
            Message_Box(title="Database Error",
                        text=f"An error occurred: {str(e)}",
                        icon="Critical")
            raise
        else:
            try:
                return self.cursor.fetchall() 
            except ProgrammingError:
                "A transaction changes the state of db, but does not return any outcome"
                self.conn.commit()
                return "Ok" # To confirm the transaction
        finally:
            self.end()

    def search_movements(self, description: str = None, date_range: tuple = None) -> list:
        """
        Search movements based on description and/or date range.
        """
        query = "SELECT * FROM movements WHERE 1=1" # (1=1) To avoid invalid SQL syntax
        params = []
        
        if description:
            query += " AND description ILIKE %s"
            params.append(f"%{description}%")
        
        if date_range:
            query += " AND date BETWEEN %s AND %s"
            params.extend(date_range)
        
        return self.execute(query, tuple(params))
    
    def start(self):
        """
        Initialize a secure database connection with proper error handling.
        """
        try:
            self.conn = psycopg2.connect(
                database=self.dbname,
                user=self.user,
                password=self.passw,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
        except psycopg2.OperationalError as e:
            Message_Box(title="Connection Error",
                        text=f"Failed to connect to database: {str(e)}",
                        icon="Critical")
            raise

    def end(self):
        """
        To finish the db connection
        """
        self.cursor.close()
        self.conn.close()
        

if __name__ == "__main__":
    conn = DB_conn(dbname="budget_planner")
    try:
        conn.start()
    except psycopg2.OperationalError:
        print("FAIL")
    else:
        conn.end()
