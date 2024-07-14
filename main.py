from database import DB_conn
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
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
        self.expense_wind = ExpenseWindow(menu=self)
        self.summ_wind = SummaryWindow(menu=self)
        self.movement.clicked.connect(lambda: self.show_window(wind='E'))
        self.exp_summary.clicked.connect(lambda: self.show_window(wind='S'))

    def show_window(self, wind: str):
        """
        It shows a windows according to the option selected
        """
        self.hide()
        if wind == 'E':
            self.expense_wind.show()
        elif wind == 'S':
            self.summ_wind.show()


class ExpenseWindow(QMainWindow, EnterExpense):
    """
    Window that shows the fields that have to be filled in to 
    record a new expense.
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.menu = menu
        self.setupUi(self)
        self.back_button.clicked.connect(self._back_menu)

    def _back_menu(self):
        """
        Return to the Budget Planner menu
        """
        self.hide()
        self.menu.show()


class SummaryWindow(QMainWindow, SummaryExp):
    """
    Window responsible of getting the expenses performed during
    a particular season and showing in a tabular way.
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.menu = menu
        self.setupUi(self)
        self.back_button.clicked.connect(self._back_menu)
        # Signal: An event that occurs and trigger the execution of a slot (function or method)
        self.seasons_cb.currentIndexChanged.connect(self._show_season_expenses)
    
    def _back_menu(self):
        """
        Return to the Budget Planner menu
        """
        self.hide()
        self.menu.show()

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
        # Add the content of the table
        model = Table(data)
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
        cols = self._months_distribution(start_year=int(season[:4]))
        idx = ["Alojamiento", "Servicios", "Comida", "Telefonia", 
                "Transporte", "Universidad","Ocio", "Gym", "Otros"]
        df_expenses = pd.DataFrame(index=idx)
        for year, month in cols:
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
        df_expenses.columns = cols
        df_expenses.fillna(0, inplace=True)
        # Add the total amount
        df_expenses = pd.concat([df_expenses, self._total_amount(df_expenses)], axis=0)
        return df_expenses

    def _months_distribution(self, start_year: int) -> list:
        """
        Get the months that are part of the season
        """
        dist_sy = pd.MultiIndex.from_product( [[start_year], list(range(7, 13))] )
        dist_fy = pd.MultiIndex.from_product( [[start_year + 1], list(range(1, 7))] )
        dist_months = dist_sy.append(dist_fy)
        return list(dist_months)

    def _total_amount(self, exp_table: pd.DataFrame) -> pd.DataFrame:
        """
        Create the record that represents the total amount of
        expenses for each month of the season.
        """
        record = pd.DataFrame(exp_table.sum(axis = 0), 
                              columns=["Total"]).T
        return record


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())