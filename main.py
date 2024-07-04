from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
import psycopg2
from windows import EnterExpense, MenuBP
import sys


class DB_Conn:
    """
    It represents the connection in the Budget Planner DB 
    """

    def __init__(self):
        with open('db_info.txt', 'r') as f:
            db_info = list(map(lambda x: x.strip(), f.read().splitlines()))
        self.active = 0
        self.database, self.user, self.password, self.host, self.port = db_info

    def start(self):
        """
        Initialize a connection with the Movement table 
        belongs to Budget Planner DB.
        """
        self.active += 1
        self.conn = psycopg2.connect(database=self.database,
                                user = self.user, 
                                password = self.password,
                                host = self.host,
                                port = self.port)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor
    
    def end(self):
        """
        It ends the connection
        """
        if self.active: 
            self.conn.close()
            self.cursor.close()
        

class MainWindow_BP(QMainWindow, MenuBP):
    """
    Main Window of the Budget Planner GUI
    """
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.movement.clicked.connect(self.enter_expense)
        self.expense_wind = ExpenseWindow()
    
    def enter_expense(self):
        """
        It calls the function that is responsible to record a new
        expense
        """
        self.close()
        self.expense_wind.show()


class ExpenseWindow(QMainWindow, EnterExpense):
    """
    Window that show the fields that have to be filled in to 
    record a new expense.
    """

    def __init__(self):
        super().__init__()
        self.db_conn = DB_Conn()
        self.setupUi(self)
        self.send_mv.clicked.connect(self._input_movement)
    
    def _input_movement(self) -> tuple:
        """
        Register a movement into the table Movements
        """
        conn, cursor = self.db_conn.start()
        record = (
            datetime.now().date().strftime("%Y-%m-%d"),
            self.options_mtype.currentText(),
            self.categories.currentText(),
            self.description.text(),
            float(self.amount.text())
        )

        query = "INSERT INTO movements (date, type, category, description, amount) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, record)
        conn.commit()
        self.db_conn.end()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())