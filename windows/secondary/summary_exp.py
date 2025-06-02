from calendar import month_name
from database import DB_conn
from datetime import datetime
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
    year into categories and shows them in tabular form. 
    """


    def setupUi(self):
        # Set the db connection
        self.db_conn = DB_conn(dbname="budget_planner")

        self.main_window.setGeometry(300, 200, 1400, 620)
        # Apply the green and gray color scheme
        self.main_window.setStyleSheet(f"background-color: #e0e0e0;")  # Light gray background
        self.centralwidget = QWidget(self.main_window)
        # It tells you what you are seeing in this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 5),
                                texto="See how much you spend over the period",
                                dimensions=(580, 80), pointsize=20, 
                                bold=True, weight=75)
        self.indication.setStyleSheet("color: #2e7d32; padding: 5px;")
        # Back button to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 60),
                             dimensions=(50, 50),                
                             mssg="⟵")
        self.back_button.clicked.connect(self._back_menu)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4caf50;
            }
        """)
        # To choose the year
        self.year_f = Field(cwidget=self.centralwidget,
                            position=(10, 140),
                            texto="Year",
                            dimensions=(145, 23))
        self.year_f.setStyleSheet("color: #2e7d32; font-weight: bold;")
        self._set_years()
        self.table = QTableView(self.main_window)
        self.table.move(50, 250)
        self.table.setGeometry(50, 250, 1295, 335)
        self.table.setStyleSheet("""
            QTableView {
                background-color: white;
                alternate-background-color: #f9f9f9;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #2e7d32;
                color: white;
                padding: 5px;
                border: 1px solid #1b5e20;
                font-weight: bold;
            }
        """)
        self.table.hide()
        self.main_window.setCentralWidget(self.centralwidget)


    def _set_years(self):
        """
        Set the available years that you can choose in order to 
        see the expenses made by categories. It will check
        the date of the first transaction (if it exists) to set
        the options for the Combobox:
        [Year of the first transaction - Currently year]
        """
        self.years_cb = ComboBox(cwidget=self.centralwidget,
                                 position=(10, 180))
        current_year = datetime.now().year
        # Get first transaction
        first_year = self.db_conn.execute("SELECT date FROM movements LIMIT 1")
        if first_year != []: # If it exists
            first_year = first_year[0][0].year # [(datetime)]
            self.years_cb.addItems([str(y) for y in range(first_year, current_year + 1)])
        else:
            self.years_cb.addItem(current_year)
        self.years_cb.currentIndexChanged.connect(self._show_table)


    def _fillin_table(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Check which months are missing from expenses table 
        to add them.
        """
        categories = ["Alojamiento", "Servicios", "Comida", "Telefonia", 
                      "Transporte", "Universidad","Ocio", "Gym", "Otros"]
        df_expenses = pd.DataFrame(0, index=categories, columns=np.arange(1, 13))
        df_expenses = df_expenses.add(data, fill_value=0) 
        # In case of nan values:
        df_expenses = df_expenses.fillna(0)
        # Add the total amount
        total_amount = pd.DataFrame(df_expenses.sum(axis = 0),
                                    columns=["Total"]).T 
        df_expenses = pd.concat([df_expenses, total_amount], axis=0)
        # Aesthetic feature: Month's names
        df_expenses.columns = [month_name[i] for i in range(1, 13)]
        return round(df_expenses, 2)


    def _qualified_records(self, year: int) -> List[Tuple[str, str, float]]:
        """
        Get those movements that belong to the year selected 
        """
        sql_cmd = f"""
        SELECT EXTRACT(MONTH FROM date), category, amount
        FROM movements
        WHERE EXTRACT(YEAR FROM date) = {year} AND  type = 'Expense'
        """
        records = [(record[0], record[1], float(record[2])) 
                    for record in self.db_conn.execute(query=sql_cmd)]
        return records
    

    def _build_table(self):
        """
        Build the table with all the expenses made in the year selected.
        """
        year_selected = self.years_cb.currentText()
        if year_selected != '': # Default option
            # Get the expenses made during that time.
            data = pd.DataFrame(self._qualified_records(year_selected), 
                                columns = ["Month", "Category", "Amount"])
            # Specify a format
            data = data.pivot_table(index = "Category", columns="Month",
                                        values="Amount", aggfunc="sum", fill_value=0)                                                                                
            # Fill in the table with the missing months
            df_expenses = self._fillin_table(data)
            return df_expenses


    def _show_table(self):
        """
        Show the expenses table according to the selected year.
        """
        # Make the corresponding transformations to the expense table
        content = self._build_table()
        if content is not None:
            # Create the model
            model = Table(content)
            self.table.setModel(model)
            self.table.show()
        elif content is None and self.table.isVisible():
            self.table.hide()


    def refresh(self):
        """
        Set the default option ('') in the season ComboBox and hide the
        year ComboBox or table or both in case they are visible
        """
        self.years_cb.setCurrentIndex(-1)
        self.table.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = SummaryExp()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())