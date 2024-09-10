import os
import psycopg2
from psycopg2.errors import CheckViolation, ProgrammingError, UniqueViolation
from typing import List
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
        self.host = os.getenv("PSQL_HOST") #"/var/run/postgresql"
        self.port = os.getenv("PSQL_PORT")

    def execute(self, commands: str | List[str]) -> list | None:
        """
        It tries to execute the sent SQL command(s). And it returns any result
        in case if it does, otherwise save the changes into the database. 
        """
        self.start()
        try:
            if type(commands) == str:
                self.cursor.execute(commands)
            else:
                for sql_cmd in commands:            
                    self.cursor.execute(sql_cmd)
        except UniqueViolation:
            Message_Box(title="Transaction Error", 
                        text="You're trying to register a record that already exists.",
                        icon="Critical")
        except CheckViolation:
            Message_Box(title="Negative balance",
                        text="The transaction cannot be completed. You don't have enough money.",
                        icon="Critical")
        else:
            try:
                return self.cursor.fetchall() 
            except ProgrammingError:
                "A transaction changes the state of db, but does not return any outcome"
                self.conn.commit()
                return "Ok" # To confirm the transaction
        finally:
            self.end()
    
    def start(self):
        """
        Initialize a connection with the Movement table 
        belongs to Budget Planner DB.
        """
        self.conn = psycopg2.connect(
            database = self.dbname,user = self.user,
            password = self.passw, host = self.host,
            port = self.port)
        self.cursor = self.conn.cursor()

    def end(self):
        """
        To finish the db connection
        """
        self.cursor.close()
        self.conn.close()
        

if __name__ == "__main__":
    conn = DB_conn(dbname="budgetplanner")
    try:
        conn.start()
    except psycopg2.OperationalError:
        print("FAIL")
    else:
        conn.end()