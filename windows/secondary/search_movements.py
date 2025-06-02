from database import DB_conn
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QDateEdit, QHeaderView
from PyQt5.QtCore import QDate
from .secondary_wind import SecondaryWindow
import sys
from widgets import Button, ComboBox, Field, InputLine, Message_Box


class SearchMovements(SecondaryWindow):
    """
    A window that allows users to search for movements based on
    description, date range, and other criteria.
    """

    def setupUi(self):
        # Set the database connection with parameterized queries
        self.db_conn = DB_conn(dbname="budget_planner")

        # Configure window
        self.main_window.setGeometry(500, 200, 900, 700)
        self.main_window.setWindowTitle("Search Movements")
        self.main_window.setStyleSheet("background-color: #f5f5f7;")
        
        self.centralwidget = QWidget(self.main_window)
        
        # Title
        self.indication = Field(cwidget=self.centralwidget, position=(10, 20),
                                texto="Search Your Financial Movements", 
                                dimensions=(700, 40), pointsize=22, 
                                bold=True, weight=75)
        self.indication.setStyleSheet("color: #2c3e50; padding: 5px;")
        
        # Back button
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 65),
                             dimensions=(50, 50),
                             mssg="⟵")
        self.back_button.clicked.connect(self._back_menu)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Search criteria section
        y_pos = 130
        
        # Description search
        self.desc_label = Field(cwidget=self.centralwidget, 
                               position=(10, y_pos),
                               dimensions=(200, 30), 
                               texto="Description contains:")
        
        self.desc_input = InputLine(cwidget=self.centralwidget, 
                                   position=(220, y_pos), 
                                   dimensions=(300, 30))
        
        # Date range
        y_pos += 60
        self.date_label = Field(cwidget=self.centralwidget, 
                               position=(10, y_pos),
                               dimensions=(200, 30), 
                               texto="Date range:")
        
        # From date
        self.from_date = QDateEdit(self.centralwidget)
        self.from_date.setGeometry(220, y_pos, 140, 30)
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        
        # To date
        self.to_label = Field(cwidget=self.centralwidget, 
                             position=(370, y_pos),
                             dimensions=(40, 30), 
                             texto="to")
        
        self.to_date = QDateEdit(self.centralwidget)
        self.to_date.setGeometry(420, y_pos, 140, 30)
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        
        # Movement type filter
        y_pos += 60
        self.type_label = Field(cwidget=self.centralwidget, 
                               position=(10, y_pos),
                               dimensions=(200, 30), 
                               texto="Movement type:")
        
        self.type_combo = ComboBox(cwidget=self.centralwidget, 
                                  position=(220, y_pos),
                                  dimensions=(200, 30),
                                  options=("", "Income", "Expense"))
        
        # Search button
        y_pos += 60
        self.search_button = Button(cwidget=self.centralwidget,
                                   position=(10, y_pos),
                                   dimensions=(200, 50),
                                   mssg="Search")
        self.search_button.clicked.connect(self._perform_search)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        # Clear button
        self.clear_button = Button(cwidget=self.centralwidget,
                                  position=(220, y_pos),
                                  dimensions=(200, 50),
                                  mssg="Clear")
        self.clear_button.clicked.connect(self.refresh)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        # Results table
        y_pos += 70
        self.results_label = Field(cwidget=self.centralwidget, 
                                  position=(10, y_pos),
                                  dimensions=(200, 30), 
                                  texto="Search Results:")
        self.results_label.setStyleSheet("font-weight: bold;")
        
        y_pos += 30
        self.results_table = QTableWidget(self.centralwidget)
        self.results_table.setGeometry(10, y_pos, 880, 300)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Date", "Type", "Category", "Description", "Amount"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
                border: 1px solid #2980b9;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        self.main_window.setCentralWidget(self.centralwidget)

    def refresh(self):
        """
        Clear all search fields and results
        """
        self.desc_input.clear()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.to_date.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)
        self.results_table.setRowCount(0)

    def _perform_search(self):
        """
        Execute search based on the provided criteria
        """
        # Build the search query with parameters
        query = "SELECT date, type, category, description, amount FROM movements WHERE 1=1"
        params = []
        
        # Add description filter if provided
        if self.desc_input.text():
            query += " AND description ILIKE %s"
            params.append(f"%{self.desc_input.text()}%")
        
        # Add date range filter
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        query += " AND date BETWEEN %s AND %s"
        params.extend([from_date, to_date])
        
        # Add movement type filter if selected
        if self.type_combo.currentText():
            query += " AND type = %s"
            params.append(self.type_combo.currentText())
        
        # Order by date, most recent first
        query += " ORDER BY date DESC"
        
        try:
            # Execute the parameterized query
            results = self.db_conn.execute(query, tuple(params))
            
            # Clear previous results
            self.results_table.setRowCount(0)
            
            if results and results != "Ok":
                # Populate the table with results
                self.results_table.setRowCount(len(results))
                
                for row_idx, row_data in enumerate(results):
                    # Format date for display
                    date_str = row_data[0].strftime("%Y-%m-%d") if isinstance(row_data[0], datetime) else str(row_data[0])
                    
                    # Format amount with currency symbol
                    amount_str = f"{row_data[4]} €"
                    
                    # Set cell values
                    self.results_table.setItem(row_idx, 0, QTableWidgetItem(date_str))
                    self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
                    self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
                    self.results_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
                    self.results_table.setItem(row_idx, 4, QTableWidgetItem(amount_str))
                    
                    # Color-code expenses in red and income in green
                    if row_data[1] == "Expense":
                        self.results_table.item(row_idx, 4).setForeground(QColor(231, 76, 60))  # Red
                    else:
                        self.results_table.item(row_idx, 4).setForeground(QColor(39, 174, 96))  # Green
            else:
                Message_Box(title="No Results",
                           text="No movements found matching your search criteria.",
                           icon="Information")
                
        except Exception as e:
            Message_Box(title="Search Error",
                       text=f"An error occurred while searching: {str(e)}",
                       icon="Critical")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = SearchMovements()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
