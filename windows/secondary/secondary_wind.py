# An abstract class serves as a blueprint for the subclasses that inherit it.
# Where they must to implement the abstract methods defined in this.
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QMainWindow


class SecondaryWindow(ABC):
    """

    Toda ventana secundaria debe contar:
     1) Con un boton que le permita retroceder hacia el menu principal
     2) Con un metodo que permita la actualizacion del contenido de la
        ventana una vez se muestre otra vez.
    """

    def __init__(self, main_window: QMainWindow, menu: QMainWindow):
        super().__init__()
        self.main_window = main_window # It represents the window itself.
        self.menu = menu
    
    def _back_menu(self):
        self.main_window.close()
        self.menu.show()

    @abstractmethod
    def refresh(self):
        """
        Once a window is reopend, clear all the fields and load the changes made 
        into the budgetplanner db to show the updated information. 
        """
        pass