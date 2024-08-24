from calendar import month_name
from database import DB_conn
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QWidget
from .secondary_wind import SecondaryWindow
import sys
from typing import List, Tuple
from widgets import Button, ComboBox, Field, Table



class SummaryExp(SecondaryWindow):
    """
    It divides the expenses I have made during a particular
    season into categories and shows them in tabular form. 
    """


    def setupUi(self):
        # Set the db connection
        self.db_conn = DB_conn(dbname="budgetplanner")

        self.main_window.setGeometry(300, 200, 1400, 620)
        self.centralwidget = QWidget(self.main_window)
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
        self.back_button.clicked.connect(self._back_menu)
        # To choose the season
        self.season_f = Field(cwidget=self.centralwidget,
                            position=(10, 140),
                            texto="Season",
                            dimensions=(145, 23))
        self._set_seasons()
        self.table = QTableView(self.main_window)
        self.table.move(50, 250)
        self.table.setGeometry(350, 250, 695, 328)
        self.table.hide()
        self.main_window.setCentralWidget(self.centralwidget)


    def _set_seasons(self):
        """
        Get all the seasons and save them into a combobox 
        """
        self.seasons_cb = ComboBox(cwidget=self.centralwidget,
                                 position=(10, 180))
        seasons = [s for s in self.db_conn.execute("SELECT sid FROM seasons")]
        # Store the value into the combobox
        self.seasons_cb.addItems([str(s[0]) for s in seasons])
        self.seasons_cb.currentIndexChanged.connect(self._add_season_details)
    

    def _add_season_details(self):
        """
        Generate the table with all the expenses of the selected season and 
        create a ComboBox that stores the years that are part of the season. 
        """
        season = self.seasons_cb.currentText()
        if season != '':
            # The columns of this table will be fitered according to the selected year.
            self._build_table(season)
            # Create the combobox that stores the years that part of the season
            self.year_field = Field(cwidget=self.centralwidget,
                                    position=(200, 140),
                                    texto="Year", 
                                    dimensions=(145, 23))
            self.year_cb = ComboBox(cwidget=self.centralwidget,
                                     position=(200, 180),
                                     options=[season[:4], f"20{season[-2:]}"])
            self.year_field.show()
            self.year_cb.show()
            self.year_cb.currentIndexChanged.connect(self._show_table)
        elif season == '':
            self.refresh()
    

    def _build_table(self, season = int):
        """
        Build the table with all the expenses made in the season.
        """
        # Get the expenses made during that time.
        data = pd.DataFrame(self._qualified_records(season), 
                            columns = ["Year", "Month", "Category", "Amount"])
        # Specify a format
        data = data.pivot_table(index = "Category", columns=["Year", "Month"],
                                       values="Amount", aggfunc="sum")
        # Fill in the table with the missing months
        self.df_expenses = self._fillin_table(data, season)


    def _qualified_records(self, season: int) -> List[Tuple[str, str, str]]:
        """
        Get those movements that belong to the season 
        """
        sql_cmd = f"""
        SELECT EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date), category, amount
        FROM movements JOIN (SELECT start, finish 
                             FROM seasons 
                             WHERE sid = {season}) AUX 
                        ON (date BETWEEN start AND finish) AND (type = 'Expense')   
        """
        return self.db_conn.execute(commands=sql_cmd)
    

    def _fillin_table(self, data: pd.DataFrame, season: int) -> pd.DataFrame:
        """
        Check which months are missing from expenses table 
        to add them.
        """
        season_months = self._months_distribution(start_year=int(season[:4]))
        for year, month in season_months:
            if (year, month) not in data.columns:
                pos = season_months.get_loc((year, month)) 
                idx = ["Alojamiento", "Servicios", "Comida", "Telefonia", 
                       "Transporte", "Universidad","Ocio", "Gym", "Otros"]
                # Each season is composed by 12 months, so once we find a month
                # where any expense was recorded, then we know that from here,
                # we have to fill the expense table.
                empty_db = pd.DataFrame(
                    np.zeros( (len(idx), 12 - data.shape[1]) ),
                    index = idx, 
                    columns = season_months[pos:])
                df_expenses = pd.merge(left=data, right=empty_db,
                                       left_index=True, right_index=True,
                                       how='outer')
                break
        df_expenses.fillna(0)
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
        dist_months.names = ["Year", "Month"]
        return dist_months


    def _total_amount(self, exp_table: pd.DataFrame) -> pd.DataFrame:
        """
        Create the record that represents the total amount of
        expenses for each month of the season.
        """
        record = pd.DataFrame(exp_table.sum(axis = 0), 
                              columns=["Total"]).T
        return record


    def _show_table(self):
        """
        Show the expenses table according to the selected year.
        """
        # Make the corresponding transformations to the expense table
        content = self._process_table()
        # Create the model
        model = Table(content)
        self.table.setModel(model)
        self.table.show()
    

    def _process_table(self) -> pd.DataFrame:
        """
        Filter the months that don't belong to the selected year and use
        the month's names instead of their number
        """
        new_table = self.df_expenses.loc[:, int(self.year_cb.currentText())]
        new_table.columns = [month_name[int(month)] for month in new_table.columns]
        return new_table
    

    def refresh(self):
        """
        Set the default option ('') in the season ComboBox and hide the
        year ComboBox or table or both in case they are visible
        """
        self.seasons_cb.setCurrentIndex(-1)
        self.table.hide()
        try:
            # When this window is open, these widgets does no exist yet.
            # It's necessary to choose a season to generate them, so this
            # could raise an exception if you select the "" at the beginning.
            self.year_field.hide()
            self.year_cb.hide()
        except AttributeError:
            pass
            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = SummaryExp()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())