import subprocess
import json
import os
import psycopg2


class DB_conn:
    """
    It represents a database connection 
    """

    def __init__(self, dbname: str):
        self.dbname = dbname
        self.host = os.getenv("PSQL_HOST")
        self.port = os.getenv("PSQL_PORT")
        self.active = False
        self.get_credentials()

    def get_credentials(self):
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
        self.active += 1
        return self.conn, self.cursor

    def end(self):
        """
        To finish the db connection
        """
        if self.active: 
            self.conn.close()
            self.cursor.close()
            self.active -= 1


if __name__ == "__main__":
    conn = DB_conn(dbname="budgetplanner")
    try:
        conn.start()
    except psycopg2.OperationalError:
        print("FAIL")
    else:
        conn.end()