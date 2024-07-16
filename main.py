from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from windows import EnterExpense, HoldingType, MenuBP, MoneyDistribution, SummaryExp
import sys
        


class MainWindow_BP(QMainWindow, MenuBP):
    """
    Main Window of the Budget Planner GUI
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.expense_wind = ExpenseWindow(menu=self)
        self.money_wind = MoneyDistWindow(menu=self)
        self.summ_wind = SummaryWindow(menu=self)
        self.movement.clicked.connect(lambda: self.show_window(wind='E'))
        self.money_dist.clicked.connect(lambda: self.show_window(wind='M'))
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
        elif wind == 'M':
            self.money_wind.show()



class ExpenseWindow(EnterExpense, QMainWindow):
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



class MoneyDistWindow(MoneyDistribution, QMainWindow):
    """
    Window that stores the amount of money that you have
    in the different holding types that you recorded.  
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.menu = menu
        self.htype_wind = HoldingWindow()
        self.add_htype.clicked.connect(self._show_htype_wind)
        self.back_button.clicked.connect(self._back_menu)
    
    def _show_htype_wind(self):
        """
        Display the window that allows you to register
        a new holding type.
        """
        self.htype_wind.show()


    def _back_menu(self):
        """
        Return to the menu
        """
        self.hide()
        self.menu.show()


class HoldingWindow(HoldingType, QMainWindow):
    """
    Window designed to add a new holding type
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)



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
        """
        self.hide()
        self.menu.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())