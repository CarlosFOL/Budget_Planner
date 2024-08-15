from PyQt5.QtWidgets import QApplication, QMainWindow
from windows import EnterExpense, HoldingType, MenuBP, MoneyDistribution, SummaryExp
import sys
        


class MainWindow_BP(MenuBP, QMainWindow):
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



class ExpenseWindow(QMainWindow):
    """
    Window that shows the fields that have to be filled in to 
    record a new expense.
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.window = EnterExpense(main_window=self, menu=menu)
        self.window.setupUi()




class MoneyDistWindow(QMainWindow):
    """
    Window that stores the amount of money that you have
    in the different holding types that you recorded.  
    """

    def __init__(self, menu: QMainWindow):
        super().__init__()
        self.window = MoneyDistribution(main_window = self, 
                                        menu=menu, 
                                        htype_wind=HoldingWindow())
        self.window.setupUi()



class HoldingWindow(QMainWindow, HoldingType):
    """
    Window designed to add a new holding type
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)



class SummaryWindow(QMainWindow):
    """
    Window responsible of getting the expenses performed during
    a particular season and showing in a tabular way.
    """

    def __init__(self, menu: QMainWindow):
        # QMainWindow.__init__(self)
        # SummaryExp.__init__(self)
        super().__init__()
        self.window = SummaryExp(main_window=self, menu=menu)
        self.window.setupUi()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow_BP()
    main_window.show()
    sys.exit(app.exec_())