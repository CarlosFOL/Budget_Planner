from database import DB_conn
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableView
from widgets import Table
from windows import EnterExpense, MenuBP, SummaryExp
import sys
        


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
    Window that shows the fields that have to be filled in to 
    record a new expense.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)



class SummaryWindow(QMainWindow, SummaryExp):
    """
    Window responsible of getting the expenses performed during
    a particular season and showing in a tabular way.
    """


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Signal: An event that occurs and trigger the execution of a slot (function or method)
        self.seasons_cb.currentIndexChanged.connect(self._show_season_expenses)


    def _show_season_expenses(self):
        """
        Build the table by getting the qualified records and
        cast it to QTableView object.
        """
        db_conn = DB_conn(dbname="budgetplanner")
        _, cursor = db_conn.start()
        season = self.seasons_cb.currentText()
        self._qualified_records(season, cursor)
        data = self._build_table(season, cursor)
        db_conn.end()
        # Add the widget
        model = Table(data)
        # table = QTableView(self.centralwidget)
        self.table.setModel(model)


    def _qualified_records(self, season: int, cursor):
        """
        Get those movements that belong to the selected season 
        """
        query = f"""
        CREATE TEMPORARY TABLE exp_table AS
        SELECT date, category, amount
        FROM movements JOIN (SELECT start, finish 
                             FROM seasons 
                             WHERE sid = {season}) AUX 
                        ON (date BETWEEN start AND finish) AND (type = 'Expense')   
        """
        cursor.execute(query)


    def _build_table(self, season: int, cursor) -> pd.DataFrame:
        """
        Build the expenses table of a particular season
        """
        columns = self._months_distribution(start_year=int(season[:4]))
        idx = ["Alojamiento", "Servicios", "Comida", "Telefonia", 
                "Transporte", "Universidad","Ocio", "Gym", "Otros"]
        df_expenses = pd.DataFrame(index=idx)
        for year, month in columns:
            query = f"""
            SELECT category, SUM(amount)
            FROM exp_table
            WHERE EXTRACT(YEAR FROM date) = {year} AND EXTRACT(MONTH FROM date) = {month}
            GROUP BY category
            """
            cursor.execute(query)
            if not cursor.rowcount == 0:
                partition = pd.DataFrame(cursor.fetchall()).set_index(0)
                df_expenses = pd.merge(left=df_expenses, 
                                     right=partition,
                                     left_index=True,
                                     right_index=True,
                                     how='outer')
            else:
                # Each column represent a month and a period is composed by 12 months.
                # Therefore, we can know in which months we don't have expenses yet.
                empty_db = pd.DataFrame(
                    np.zeros( (len(idx), 12 - df_expenses.shape[1]) ),
                    index = idx
                    )
                df_expenses = pd.merge(left=df_expenses,
                                     right=empty_db,
                                     left_index=True,
                                     right_index=True,
                                     how='outer')
                break
        df_expenses.columns = columns
        df_expenses.fillna(0, inplace=True)
        return df_expenses.reset_index()


    def _months_distribution(self, start_year: int) -> pd.MultiIndex:
        """
        Get the months that are part of the season
        """
        dist_sy = pd.MultiIndex.from_product( [[start_year], list(range(7, 13))] )
        dist_fy = pd.MultiIndex.from_product( [[start_year + 1], list(range(1, 7))] )
        dist_months = dist_sy.append(dist_fy)
        return dist_months



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())