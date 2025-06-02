#!/home/carlosfol/Desktop/Git_Projects/Budget_Planner/venv_bp/bin/python3
from PyQt5.QtWidgets import QApplication, QMainWindow
from windows import MenuBP, EnterExpense, MoneyDistribution, SearchMovements, SummaryExp, TransferMoney
import sys
        

class MainWindow_BP(MenuBP, QMainWindow):
    """
    Main Window of the Budget Planner GUI

    Attributes:
        expense_wind (ExpenseWindow): 
            The window for entering expenses
        money_wind (MoneyDistWindow): 
            The window for managing money distributions
        summ_wind (SummaryWindow): 
            The window for summarizing expenses
        search_wind (SearchWindow): 
            The window for searching movements
    
    Methods:
        show_window(wind: str): 
            It shows a window according to the option selected
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.expense_wind = ExpenseWindow(menu=self)
        self.money_wind = MoneyDistWindow(menu=self)
        self.summ_wind = SummaryWindow(menu=self)
        self.search_wind = SearchWindow(menu=self)
        
        # Connect buttons to their respective windows
        self.movement.clicked.connect(lambda: self.show_window(wind='E'))
        self.money_dist.clicked.connect(lambda: self.show_window(wind='M'))
        self.exp_summary.clicked.connect(lambda: self.show_window(wind='S'))
        self.search_btn.clicked.connect(lambda: self.show_window(wind='F'))

    def show_window(self, wind: str):
        """
        It shows a window according to the option selected

        Args:
            wind (str): 
                The option selected
        """
        self.hide()
        if wind == 'E':
            self.expense_wind.clear_fields()
            self.expense_wind.show()
        elif wind == 'M':
            self.money_wind.update_balances()
            self.money_wind.show()
        elif wind == 'S':
            self.summ_wind.clear_fields()
            self.summ_wind.show()
        elif wind == 'F':
            self.search_wind.clear_fields()
            self.search_wind.show()



class ExpenseWindow(QMainWindow):
    """
    Window that shows the fields that have to be filled in to 
    record a new expense.

    Attributes:
        menu (QMainWindow): 
            The main window
        window (EnterExpense): 
            The window for entering expenses

    Methods:
        clear_fields(): 
            Clear all the fields once this window is reopened
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.window = EnterExpense(main_window=self, menu=menu)
        self.window.setupUi()
    
    def clear_fields(self):
        """
        Clear all the fields once this window is reopened
        """
        self.window.refresh()



class MoneyDistWindow(QMainWindow):
    """
    Window that stores the amount of money that you have
    in the different holding types that you recorded.  

    Attributes:
        menu (QMainWindow): 
            The main window
        window (MoneyDistribution): 
            The window for managing money distributions

    Methods:
        update_balances(): 
            It updates the balances of the htypes once this window is open
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.window = MoneyDistribution(main_window = self, 
                                        menu=menu, 
                                        htype_wind=HoldingWindow(),
                                        trasnfer_wind=TransferWindow())
        self.window.setupUi()
    
    def update_balances(self):
        """
        It updates the balances of the htypes once this window is open.
        """
        self.window.refresh()


class HoldingWindow(QMainWindow, HoldingType):
    """
    Window designed to add a new holding type

    Attributes:
        menu (QMainWindow): 
            The main window
        window (HoldingType): 
            The window for adding a new holding type
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class TransferWindow(QMainWindow, TransferMoney):
    """
    Window designed to transfer money from one holding type to another

    Attributes:
        menu (QMainWindow): 
            The main window
        window (TransferMoney): 
            The window for transferring money between holding types
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)



class SummaryWindow(QMainWindow):
    """
    Window responsible of getting the expenses performed during
    a particular season and showing in a tabular way.
    
    Attributes:
        menu (QMainWindow): 
            The main window
        window (SummaryExp): 
            The window for summarizing expenses

    Methods:
        clear_fields(): 
            Only show the season ComboBox with the default value ('') settled.
    """

    def __init__(self, menu: QMainWindow):
        # QMainWindow.__init__(self)
        # SummaryExp.__init__(self)
        super().__init__()
        self.window = SummaryExp(main_window=self, menu=menu)
        self.window.setupUi()
    

    def clear_fields(self):
        """
        Only show the season ComboBox with the default value ('') settled.
        """
        self.window.refresh()
        


class SearchWindow(QMainWindow):
    """
    Window that allows searching for movements based on description,
    date range, or other criteria.

    Attributes:
        menu (QMainWindow): 
            The main window
        window (SearchMovements): 
            The window for searching movements

    Methods:
        clear_fields(): 
            Clear all the search fields when this window is reopened
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.window = SearchMovements(main_window=self, menu=menu)
        self.window.setupUi()
    
    def clear_fields(self):
        """
        Clear all the search fields when this window is reopened
        """
        self.window.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())
