import subprocess
import json
import os
import psycopg2
from psycopg2.errors import CheckViolation, ProgrammingError, UniqueViolation
from typing import List
import os
os.chdir("..")
from widgets import Message_Box


class DB_conn:
    """
    It represents a database connection 
    """

    def __init__(self, dbname: str):
        self.dbname = dbname
        self.host = os.getenv("PSQL_HOST")
        self.port = os.getenv("PSQL_PORT")
        self._get_credentials()

    def _get_credentials(self):
        """
        Obtain the user and password to connec to the 
        budget planner database
        """
        creds_path = os.getenv("PSQL_CREDS")
        data = subprocess.run(["gpg", "--decrypt", creds_path], 
                              capture_output=True,
                              text = True, 
                              check = True)
        credentials = json.loads(data.stdout)
        self.user = credentials["user"]
        self.passw = credentials["pass"]

    def execute(self, commands: str | List[str], end_conn=True) -> list | None:
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
            if end_conn:
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
        self.conn.close()
        self.cursor.close()


if __name__ == "__main__":
    conn = DB_conn(dbname="budgetplanner")
    try:
        conn.start()
    except psycopg2.OperationalError:
        print("FAIL")
    else:
        conn.end()