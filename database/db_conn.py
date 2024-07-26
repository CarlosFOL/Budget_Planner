import subprocess
import json
import os
from PyQt5.QtWidgets import QMessageBox
import psycopg2
from psycopg2.errors import ProgrammingError, UniqueViolation  


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

    def execute(self, sql_command: str, parameters: tuple = None):
        """
        Execute the SQL command and return its outcome in case
        if it does. 
        """
        self.start()
        mssg = QMessageBox()
        try:
            if parameters is not None:
                self.cursor.execute(sql_command, parameters)
            else:
                self.cursor.execute(sql_command)
        except UniqueViolation:
            mssg.setText("You're trying to register a record that already exists.")
        else:
            try:
                return self.cursor.fetchall()
            except ProgrammingError:
                "A transaction changes the state of db, but does not return any outcome"
                self.conn.commit()
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