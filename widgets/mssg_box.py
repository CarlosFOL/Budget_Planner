from PyQt5.QtWidgets import QMessageBox


class Message_Box(QMessageBox):
    """
    Pop-up window that shows a message that indicates 
    the status of an perfomed operation in the database
    """

    def __init__(self, title: str, text: str, icon: str):
        super().__init__()
        self.title = title
        self.text = text
        self.icon = icon
        self._setUp()
    
    def _setUp(self):
        """
        Set the main features
        """
        icons = {"Critical": QMessageBox.Critical, "Information": QMessageBox.Information}
        self.setWindowTitle(self.title)
        self.setText(self.text)
        self.setIcon(icons[self.icon])
        # To display it
        x = self.exec_()