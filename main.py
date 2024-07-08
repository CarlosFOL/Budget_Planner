from datetime import datetime
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
import psycopg2
from windows import EnterExpense, MenuBP, SummaryExp
import sys


class DB_Conn:
    """
    It represents the connection in the Budget Planner DB 
    """

    def __init__(self):
        with open('db_info.txt', 'r') as f:
            self.db_info = list(map( lambda x: x.strip(), f.read().splitlines()) )
        self.active = 0

    def start(self):
        """
        Initialize a connection with the Movement table 
        belongs to Budget Planner DB.
        """
        keys = ['database', 'user', 'password', 'host', 'port']
        data = {k: v for k, v in zip(keys, self.db_info)}
        self.conn = psycopg2.connect(**data)
        self.cursor = self.conn.cursor()
        self.active += 1
        return self.conn, self.cursor
    
    def end(self):
        """
        It ends the connection
        """
        if self.active: 
            self.conn.close()
            self.cursor.close()
            self.active -= 1
        

class MainWindow_BP(QMainWindow, MenuBP):
    """
    Main Window of the Budget Planner GUI
    """
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.expense_wind = ExpenseWindow()
        self.summ_wind = SummaryWindow()
        self.movement.clicked.connect(lambda: self.show_window(wind='E'))
        self.exp_summary.clicked.connect(lambda: self.show_window(wind='S'))
    
    def show_window(self, wind: str):
        """
        """
        self.close()
        if wind == 'E':
            self.expense_wind.show()
        elif wind == 'S':
            self.summ_wind.show()


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
        # Remove the content of the fields
        self.description.clear()
        self.amount.clear()

class SummaryWindow(QMainWindow, SummaryExp):
    """
    """

    def __init__(self):
        super().__init__()
        self.db_conn = DB_Conn()
        self.setupUi(self)
        self._set_options()
        # Signal: An event that occurs and trigger the execution of a slot
        # Slot: A function or method
        self.seasons_cb.currentIndexChanged.connect(self._build_exp_table)
    
    def _set_options(self):
        """
        Get the options that we can select when we click 
        on the Season combo box.  
        """
        _, cursor = self.db_conn.start()
        cursor.execute("SELECT sid FROM seasons")
        seasons = [str(s[0]) for s in cursor.fetchall()]
        self.seasons_cb.addItems(seasons)
        self.db_conn.end()

    def _build_exp_table(self):
        """
        """
        _, cursor = self.db_conn.start()
        season = self.seasons_cb.currentText()
        temp = f"""
        CREATE TEMPORARY TABLE exp_table AS
        SELECT date, category, amount
        FROM movements JOIN (SELECT start, finish 
                             FROM seasons 
                             WHERE sid = {season}) AUX 
                        ON (date BETWEEN start AND finish) AND (type = 'Expense')   
        """
        cursor.execute(temp)
        start_year = int(season[:4])
        # Months distribution (sy -> start year & fy -> finish year)
        dist_sy = pd.MultiIndex.from_product( [[start_year], list(range(7, 13))] )
        dist_fy = pd.MultiIndex.from_product( [[start_year + 1], list(range(1, 7))] )
        dist_months = dist_sy.append(dist_fy)
        # Building the expense table
        expenses = ["Alojamiento", "Servicios", "Comida", "Telefonia", 
                    "Transporte", "Universidad","Ocio", "Gym", "Otros"]
        exp_table = pd.DataFrame(index=expenses)
        for year, month in dist_months:
            part = f"""
            SELECT category, SUM(amount)
            FROM exp_table
            WHERE EXTRACT(YEAR FROM date) = {year} AND EXTRACT(MONTH FROM date) = {month}
            GROUP BY category
            """
            cursor.execute(part)
            if not cursor.rowcount == 0:
                partition = pd.DataFrame(cursor.fetchall()).set_index(0)
                exp_table = pd.merge(left=exp_table, 
                                     right=partition,
                                     left_index=True,
                                     right_index=True,
                                     how='outer')
            else:
                # Each column represent a month and a period is composed by 12 months.
                # Therefore, we can know in which months we don't have expenses yet.
                empty_db = pd.DataFrame(
                    np.zeros( (len(expenses), 12 - exp_table.shape[1]) ),
                    index = expenses
                    )
                exp_table = pd.merge(left=exp_table,
                                     right=empty_db,
                                     left_index=True,
                                     right_index=True,
                                     how='outer')
                break
        exp_table.columns = dist_months
        exp_table.fillna(0, inplace=True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())