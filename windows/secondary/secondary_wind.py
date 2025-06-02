from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QMainWindow


class SecondaryWindow(ABC):
    """
    Base class for all secondary windows in the Budget Planner application.
    
    Every secondary window must have:
     1) A button to go back to the main menu
     2) A method to refresh the content when the window is shown again
    
    Attributes:
        main_window (QMainWindow): 
            The main window of the application.
        menu (QMainWindow): 
            The menu window of the application.

    Methods:
        setupUi(): 
            Sets up the user interface for the secondary window.
        refresh(): 
            Refreshes the content of the secondary window.
    """
    # Standard color scheme for all secondary windows
    COLORS = {
        'background': '#e0e0e0',  # Light gray background
        'primary': '#2e7d32',    # Dark green for primary elements
        'secondary': '#4caf50',  # Medium green for secondary elements
        'light': '#81c784',      # Light green for highlights
        'text': '#212121',       # Dark gray for text
        'text_light': '#ffffff'  # White for text on dark backgrounds
    }
    
    # Standard button style
    BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_light']};
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {COLORS['secondary']};
        }}
    """

    def __init__(self, main_window: QMainWindow, menu: QMainWindow):
        super().__init__()
        self.main_window = main_window  # It represents the window itself.
        self.menu = menu
        
        # Apply standard styling to the window
        self.main_window.setStyleSheet(f"background-color: {self.COLORS['background']};")
    
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