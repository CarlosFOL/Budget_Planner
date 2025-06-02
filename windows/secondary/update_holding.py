from database import DB_conn
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from widgets import Button, ComboBox, Field, InputLine, Message_Box
from .secondary_wind import SecondaryWindow
import sys


class UpdateHolding(SecondaryWindow):
    """
    A window to update the amount of a specific financial holding.
    """
    
    def __init__(self, main_window: QMainWindow, parent_window: QMainWindow):
        super().__init__(main_window, parent_window)
        self.holding_type = ""
        self.institution = ""
        self.current_amount = 0.0
    
    def setupUi(self):
        # Set the database connection
        self.db_conn = DB_conn(dbname="budget_planner")
        
        # Window properties
        self.main_window.setGeometry(500, 300, 400, 300)
        self.main_window.setWindowTitle("Update Financial Holding")
        self.main_window.setStyleSheet("background-color: #e0e0e0;")  # Light gray background
        self.centralwidget = QWidget(self.main_window)
        
        # Title
        self.title = Field(cwidget=self.centralwidget, position=(20, 20),
                           texto="Update Financial Holding", 
                           dimensions=(360, 45), pointsize=18, 
                           bold=True, weight=75)
        self.title.setStyleSheet("color: #2e7d32; padding: 5px;")
        
        # Holding type selection
        self.htype_label = Field(cwidget=self.centralwidget, position=(20, 80),
                                texto="Holding Type:", 
                                dimensions=(150, 30), bold=True)
        self.htype_label.setStyleSheet("color: #2e7d32;")
        
        self.htype_combo = ComboBox(cwidget=self.centralwidget, 
                                   position=(180, 80),
                                   dimensions=(180, 30))
        
        # Institution selection (only visible for Card type)
        self.inst_label = Field(cwidget=self.centralwidget, position=(20, 120),
                               texto="Institution:", 
                               dimensions=(150, 30), bold=True)
        self.inst_label.setStyleSheet("color: #2e7d32;")
        
        self.inst_combo = ComboBox(cwidget=self.centralwidget, 
                                  position=(180, 120),
                                  dimensions=(180, 30))
        
        # Current amount display
        self.current_label = Field(cwidget=self.centralwidget, position=(20, 160),
                                 texto="Current Amount:", 
                                 dimensions=(150, 30), bold=True)
        self.current_label.setStyleSheet("color: #2e7d32;")
        
        self.current_amount_field = Field(cwidget=self.centralwidget, position=(180, 160),
                                        texto="0.00 €", 
                                        dimensions=(180, 30))
        
        # New amount input
        self.new_label = Field(cwidget=self.centralwidget, position=(20, 200),
                             texto="New Amount:", 
                             dimensions=(150, 30), bold=True)
        self.new_label.setStyleSheet("color: #2e7d32;")
        
        self.new_amount = InputLine(cwidget=self.centralwidget, 
                                   position=(180, 200),
                                   dimensions=(180, 30),
                                   regex=r'^\d{1,4}(\.\d{0,2})?$')
        
        # Update button
        button_style = """
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4caf50;
            }
        """
        
        self.update_button = Button(cwidget=self.centralwidget,
                                   position=(200, 240),
                                   dimensions=(160, 40),
                                   mssg="Update Amount")
        self.update_button.clicked.connect(self._update_amount)
        self.update_button.setStyleSheet(button_style)
        
        # Cancel button
        self.cancel_button = Button(cwidget=self.centralwidget,
                                  position=(20, 240),
                                  dimensions=(160, 40),
                                  mssg="Cancel")
        self.cancel_button.clicked.connect(self._back_menu)
        self.cancel_button.setStyleSheet(button_style)
        
        # Initialize
        self.main_window.setCentralWidget(self.centralwidget)
        self.load_holding_types()
        
        # Connect signals
        self.htype_combo.currentIndexChanged.connect(self._on_htype_changed)
        self.inst_combo.currentIndexChanged.connect(self._update_current_amount)
    
    def refresh(self):
        """
        Clear all fields and reload data from database
        """
        # Clear all fields
        self.htype_combo.clear()
        self.inst_combo.clear()
        self.new_amount.clear()
        self.current_amount_field.setText("0.00 €")
        
        # Hide institution fields initially
        self.inst_label.hide()
        self.inst_combo.hide()
        
        # Reload holding types
        self.load_holding_types()
    
    def load_holding_types(self):
        """Load available holding types from database"""
        query = "SELECT DISTINCT holding_type FROM financial_holdings"
        response = self.db_conn.execute(query)
        
        if response and response != "Error":
            htypes = [record[0] for record in response]
            self.htype_combo.addItems(htypes)
    
    def _on_htype_changed(self):
        """Handle holding type selection change"""
        self.holding_type = self.htype_combo.currentText()
        
        # Clear institution combo and hide if not needed
        self.inst_combo.clear()
        
        if self.holding_type == "Card":
            # Show institution selector and load institutions
            self.inst_label.show()
            self.inst_combo.show()
            
            query = "SELECT DISTINCT institution FROM financial_holdings WHERE holding_type = %s"
            response = self.db_conn.execute(query, (self.holding_type,))
            
            if response and response != "Error":
                institutions = [record[0] for record in response if record[0] is not None]
                self.inst_combo.addItems(institutions)
        else:
            # Hide institution selector for Cash
            self.inst_label.hide()
            self.inst_combo.hide()
            self._update_current_amount()
    
    def _update_current_amount(self):
        """Update the current amount display based on selection"""
        self.holding_type = self.htype_combo.currentText()
        
        if not self.holding_type:
            return
            
        if self.holding_type == "Card":
            self.institution = self.inst_combo.currentText()
            if not self.institution:
                return
                
            query = "SELECT amount FROM financial_holdings WHERE holding_type = %s AND institution = %s"
            params = (self.holding_type, self.institution)
        else:  # Cash
            query = "SELECT amount FROM financial_holdings WHERE holding_type = %s"
            params = (self.holding_type,)
        
        response = self.db_conn.execute(query, params)
        
        if response and response != "Error" and len(response) > 0:
            self.current_amount = float(response[0][0])
            self.current_amount_field.setText(f"{self.current_amount:.2f} €")
    
    def _update_amount(self):
        """Update the amount in the database"""
        new_amount_text = self.new_amount.text().strip()
        
        # Validate input
        if not new_amount_text:
            Message_Box(title="Input Error",
                       text="Please enter a new amount",
                       icon="Warning")
            return
            
        try:
            new_amount = float(new_amount_text)
            
            # Check for negative values
            if new_amount < 0:
                Message_Box(title="Input Error",
                           text="Amount cannot be negative",
                           icon="Warning")
                return
                
            # Update the database
            if self.holding_type == "Card":
                query = "UPDATE financial_holdings SET amount = %s WHERE holding_type = %s AND institution = %s"
                params = (new_amount, self.holding_type, self.institution)
            else:  # Cash
                query = "UPDATE financial_holdings SET amount = %s WHERE holding_type = %s"
                params = (new_amount, self.holding_type)
                
            result = self.db_conn.execute(query, params)
            
            if result == "Ok":
                Message_Box(title="Update Successful",
                           text=f"Amount for {self.holding_type} {self.institution if self.institution else ''} updated successfully",
                           icon="Information")
                self._back_menu()  # Return to parent window
            else:
                Message_Box(title="Update Failed",
                           text="Failed to update the amount",
                           icon="Warning")
                
        except ValueError:
            Message_Box(title="Input Error",
                       text="Invalid amount format",
                       icon="Warning")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UpdateHolding(MainWindow, MainWindow)
    ui.setupUi()
    MainWindow.show()
    sys.exit(app.exec_())
