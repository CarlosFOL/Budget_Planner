from database import DB_conn
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QWidget
from widgets import Button, ComboBox, Field, Table
import sys



class SummaryExp(object):
    """
    It divides the expenses I have made during a particular
    season into categories and shows them in tabular form. 
    """


    def setupUi(self, MainWindow):
        # Set the db connection
        self.db_conn = DB_conn(dbname="budgetplanner")

        MainWindow.setGeometry(300, 200, 1400, 620)
        self.centralwidget = QWidget(MainWindow)
        # It tells you what you are seeing in this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 5),
                                texto="See how much you spend over the period",
                                dimensions=(550, 40), pointsize=20, 
                                bold=True, weight=75)
        # Back button to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 60),
                             dimensions=(50, 50),                
                             mssg="⟵")
        # To choose the season
        self.season_f = Field(cwidget=self.centralwidget,
                            position=(10, 140),
                            texto="Season",
                            dimensions=(145, 23))
        self._set_seasons()
        self.table = QTableView(MainWindow)
        self.table.setGeometry(50, 250, 1295, 325)
        MainWindow.setCentralWidget(self.centralwidget)


    def _set_seasons(self):
        """
        Get all the seasons and save them into a combobox 
        """
        self.seasons_cb = ComboBox(cwidget=self.centralwidget,
                                 position=(10, 180))
        seasons = [s for s in self.db_conn.execute("SELECT sid FROM seasons")]
        # Store the value into the combobox
        if len(seasons) == 1: # if it only returns 1 season
            self.seasons_cb.addItem(str(seasons[0][0])) # Structure: [(202425,)]
        else:
            self.seasons_cb.addItems([str(s[0]) for s in seasons])
        self.seasons_cb.currentIndexChanged.connect(self._show_season_expenses)
    

    def _show_season_expenses(self):
        """
        Build the table by getting the qualified records and
        cast it to QTableView object.
        """
        season = self.season_cb.currentText()
        # Create the temporary table with the records belong to the selected season
        self._qualified_records(season)
        # Build the table with the expenses of each month and organized by category  
        data = self._build_table(season)
        # Add the content
        model = Table(data)
        self.table.setModel(model)


    def _qualified_records(self, season: int):
        """
        Get those movements that belong to the selected season 
        """
        sql_cmd = f"""
        CREATE TEMPORARY TABLE exp_table AS
        SELECT date, category, amount
        FROM movements JOIN (SELECT start, finish 
                             FROM seasons 
                             WHERE sid = {season}) AUX 
                        ON (date BETWEEN start AND finish) AND (type = 'Expense')   
        """
        # To not kill the db session
        self.db_conn.execute(commands=sql_cmd, end_conn=False)


    def _build_table(self, season: int) -> pd.DataFrame:
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
            response = self.db_conn.execute(commands=query, end_conn=False)
            if len(response) != 0:
                partition = pd.DataFrame(response.set_index(0))
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
        # Once the data is retrieved
        self.db_conn.end()
        
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
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = SummaryExp()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())