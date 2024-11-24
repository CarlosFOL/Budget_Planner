from database import DB_conn
from datetime import datetime
from functools import reduce
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from widgets import Button, ComboBox, Field, InputLine, Message_Box
from .secondary_wind import SecondaryWindow
import sys



class MoneyDistribution(SecondaryWindow):
    """
    A window where you can see how much money you have save
    in cash and in cards.
    """


    def __init__(self, main_window: QMainWindow, menu: QMainWindow, 
                 htype_wind: QMainWindow, trasnfer_wind: QMainWindow):
        super().__init__(main_window, menu)
        self.htype_wind = htype_wind
        self.transfer_wind = trasnfer_wind


    def setupUi(self):
        # Set the database connection
        self.db_conn = DB_conn(dbname="budget_planner")

        self.main_window.setGeometry(500, 200, 750, 700)
        self.centralwidget = QWidget(self.main_window)
        # Get the htypes that were added to the financial holding table
        # It tells you what you are seeing in this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 20),
                                texto="Have a look at how much money you have", 
                                dimensions=(590, 32), pointsize=20, 
                                bold=True, weight=75)
        # To return to the menu
        self.back_button = Button(cwidget=self.centralwidget, 
                             position=(10, 65),
                             dimensions=(50, 50),
                             mssg="⟵")
        self.back_button.clicked.connect(self._back_menu)
        # To add and remove and holding type
        bsize = (175, 50) # Button's size
        self.add_htype = Button(cwidget=self.centralwidget,
                                position=(10, 140),
                                dimensions=bsize,
                                mssg="Add Holding")
        self.add_htype.clicked.connect(lambda: self._show_window("A"))
        self.rm_htype = Button(cwidget=self.centralwidget,
                               position=(200, 140),
                               dimensions=bsize,
                               mssg="Remove Holding")
        # To transfer money between the holding types
        self.transfer = Button(cwidget=self.centralwidget,
                               position=(500, 140),
                               dimensions=(50, 50),
                               mssg='⇅')
        self.transfer.clicked.connect(lambda: self._show_window("T"))
        self.refresh()
        self.main_window.setCentralWidget(self.centralwidget)
    

    def _show_window(self, window: str):
        """
        Depending to the name of the window, it displays a window for:
        * (A): Add a new holding type.
        * (T): Tranfer money between the registered holding types.
        """
        if window == "A":
            self.htype_wind.refresh()
            self.htype_wind.show()
        elif window == "T":
            self.transfer_wind.refresh()
            self.transfer_wind.show()


    def refresh(self):
        """
        It checks if there are htypes that have been added in order
        to show them in this window.
        """
        # We put them in their original position
        self.add_htype.move(10, 140)
        self.rm_htype.move(200, 140)
        self.transfer.move(500, 140)
        # Retrieve the registered holding types
        records = self.db_conn.execute("SELECT holding_type, institution, amount\
                                        FROM financial_holdings")
        # Create a section for each holding type.
        ycoord = self.add_htype.y()
        for htype in ["Card", "Cash"]:
            match_records = [r for r in records if r[0] == htype]
            if len(match_records) > 0:
                ycoord = self._create_section(htype, match_records, ycoord)    
        self._get_total_amount(records, ycoord)                
        
    
    def _create_section(self, htype: str, match_rec: list | tuple, ycoord: int) -> int:
        """
        Create a section for a particular htype. 
        """
        Field(cwidget=self.centralwidget, position=(10, ycoord),
              dimensions=(400, 30), texto=f"<u> {htype} </u>", bold=True, 
              pointsize=18, weight=75)
        sep = 40 # Separator of widgets
        if htype == "Card":
            for m_rec in match_rec:
                Field(cwidget=self.centralwidget, position=(10, ycoord + sep),
                          dimensions=(300, 50), texto=m_rec[1])
                InputLine(cwidget=self.centralwidget, position=(10, ycoord + 2*sep), 
                              texto=f"{str(m_rec[-1])} €", readonly=True)
                ycoord += 2*sep
        elif htype == "Cash":
            # If this holding type was registered, then there is only 1 record within
            # the matching records.
            record = match_rec[0]
            InputLine(cwidget=self.centralwidget, position=(10, ycoord + sep),
                      texto=f"{str(record[-1])} €", readonly=True)
            ycoord += sep
        return ycoord + 2*sep


    def _get_total_amount(self, records: list | tuple, ycoord):
        """
        Calculate the accumulative sum of the amounts of 
        the registered htypes  
        """
        Field(cwidget=self.centralwidget, position=(10, ycoord),
              dimensions=(300, 50), texto="TOTAL:", bold=True, 
              pointsize=20, weight=75)
        if len(records) != 0:
            text = reduce(lambda a1, a2: a1 + a2, [r[-1] for r in records])
        else:
            text = 0
        InputLine(cwidget=self.centralwidget, position=(112, ycoord + 5), 
                  texto=f"{text} €", readonly=True)
        # Adjust the position of the buttons to add or remove a htype
        self.add_htype.move(self.add_htype.x(), ycoord + 90)
        self.rm_htype.move(self.rm_htype.x(), ycoord + 90)
        self.transfer.move(self.transfer.x(), ycoord + 90)



class HoldingType:
    """
    Special window to register a new holding type
    """


    def setupUi(self, MainWindow: QMainWindow):
        # Set the db connection
        self.db_conn = DB_conn(dbname="budget_planner")

        MainWindow.setGeometry(600, 200, 500, 450)
        self.centralwidget = QWidget(MainWindow)
        # It tells you what you are seeing in this window
        self.indication = Field(cwidget=self.centralwidget, position=(10, 10),
                                texto="Fill in the field of the new holding type",
                                dimensions=(400, 32),bold=True, weight=75)
        # Set a htype: cash, card, investment, etc
        self.htype = Field(cwidget=self.centralwidget, position=(10, 60),
                           texto="Holding Type", dimensions=(200, 30))
        self.htype_cb = ComboBox(cwidget=self.centralwidget, position=(10, 100),
                                 options=("Cash", "Card"))
        # The rest of the fields
        self.institution = Field(cwidget=self.centralwidget, position=(10, 160),
                                     texto="Institution", dimensions=(200, 30))
        self.input_inst = InputLine(cwidget=self.centralwidget, position=(10, 200), 
                                     max_char=9)
        self.amount = Field(cwidget=self.centralwidget, position=(10, 260),
                            texto="Amount", dimensions=(200, 30))
        self.input_amount = InputLine(cwidget=self.centralwidget, position=(10, 300),
                                      regex=r'^\d{1,4}(\.\d{0,2})?$')
        # Save a new holding type
        self.save_htype = Button(cwidget=self.centralwidget,
                                 position=(10, 380),
                                 dimensions=(100, 40),
                                 mssg="Save")
        self.save_htype.clicked.connect(self._save_new_htype)
        # Hide them
        self._toggle_visibility(self.institution, self.input_inst, 
                                self.amount, self.input_amount, 
                                self.save_htype, hide=True)
        # Show the corresponding fields
        self.htype_cb.currentIndexChanged.connect(self._show_more_fields)
        MainWindow.setCentralWidget(self.centralwidget)


    def refresh(self):
        """
        Clear the fields in order to add the information of the new holding type.
        """
        self.htype_cb.setCurrentIndex(-1)


    def _show_more_fields(self):
        """
        According to the holding type selected, it will display
        all the rest of the widgets or only some of them.
        """
        option = self.htype_cb.currentText()
        if option == "Card":
            # Rearrange the widgets
            self.amount.move(10, self.institution.y() + 100)
            self.input_amount.move(10, self.input_inst.y() + 100)
            self._toggle_visibility(self.institution, self.input_inst, 
                                    self.amount, self.input_amount, self.save_htype)
        elif option == "Cash":
            # Rearrange the widgets
            self.amount.move(10, self.institution.y())
            self.input_amount.move(10, self.input_inst.y())
            self._toggle_visibility(self.institution, self.input_inst, hide=True)
            self._toggle_visibility(self.amount, self.input_amount, self.save_htype)
        elif option == '':
            self._toggle_visibility(self.institution, self.input_inst, 
                                    self.amount, self.input_amount, self.save_htype, hide=True)
        self.save_htype.move(10, self.input_amount.y() + 80)


    def _toggle_visibility(self, *args, hide = False):
        """
        To hide or display the sent widgets.
        """
        if hide:
            for field in args:
                field.hide()
        else:
            for field in args:
                field.show()
    

    def _save_new_htype(self):
        """
        Once a button is clicked, the new htype is stored in the
        financial holding table
        """
        inputs = (
            self.htype_cb.currentText(),
            self.input_inst.text() if len(self.input_inst.text()) != 0 else None,
            self.input_amount.text(),
            datetime.now().date().strftime("%Y-%m-%d")
            )
        self.db_conn.execute("INSERT INTO financial_holdings (holding_type, institution, amount, last_updated) \
                              VALUES ('%s', '%s', %s, '%s')"%inputs)
    

    def _clear_fields(self):
        """
        Clear all the fields once the new holding type is stored
        """
        self.input_inst.clear()
        self.input_amount.clear()



class TransferMoney:
    """
    This window allows you to transfer a certain amount of money
    between the different holding types that were registered
    in the table financial_holding in the budgetplanner db.
    """


    def setupUi(self, MainWindow: QMainWindow):
        # Set the db connection
        self.db_conn = DB_conn(dbname="budget_planner")

        MainWindow.setGeometry(600, 200, 500, 480)
        self.centralwidget = QWidget(MainWindow)

        x = 10
        # To indicate what to do in this window
        self.indication = Field(cwidget=self.centralwidget, 
                                texto="Let's transfer money.", 
                                position=(x, 10), 
                                dimensions=(400, 32), 
                                bold=True, 
                                weight=75)
        # Set the origin
        self.origin = Field(cwidget=self.centralwidget, 
                            position=(x, 60),
                            texto="<u>ORIGIN</u>",
                            dimensions=(200, 30))
        self.or_htypes = ComboBox(cwidget=self.centralwidget, 
                                  position=(x, self.origin.y() + 40))
        # Set the amount of monet that will be transfered
        self.amount = InputLine(cwidget=self.centralwidget, 
                                position=(x, self.or_htypes.y() + 100),
                                regex=r'^\d{1,4}(\.\d{0,2})?$', 
                                dimensions=(141, 41))
        self.currency = Field(cwidget=self.centralwidget, 
                              position=(self.amount.x() + 120 ,self.amount.y() + 5),
                              texto="€", 
                              dimensions=(200, 30))
        # Set the destination
        self.dest = Field(cwidget=self.centralwidget, 
                          position=(x, self.amount.y() + 100),
                          texto="<u>DESTINATION</u>", 
                          dimensions=(200, 30))
        self.dest_htypes = ComboBox(cwidget=self.centralwidget, 
                                    position=(x, self.dest.y() + 40))
        # To add aesthetic features
        for y_coord, sign in [(self.or_htypes.y(), 1), (self.dest.y(), -1)]:
            Field(cwidget=self.centralwidget, position=(60, y_coord + (50 * sign)),
                  texto='↓', dimensions=(200, 40), 
                  bold=True, weight=75, pointsize=40)
        self._data_management()
        # Save the transfer and modify the balances of the htypes implied. 
        self.transfer = Button(cwidget=self.centralwidget, 
                               position=(x, self.dest_htypes.y() + 70),
                               dimensions=(120, 40), 
                               mssg="TRANSFER")
        self.transfer.clicked.connect(self._perform_the_transfer)
        MainWindow.setCentralWidget(self.centralwidget)


    def refresh(self):
        """
        Clear the fields to perform a new transaction between the 
        registeres holding types.
        """
        self.or_htypes.setCurrentIndex(-1)


    def _data_management(self):
        """
        The data stored in the table financial holding is assigned
        to the combo boxes of both origin and destination. 
        """
        response = self.db_conn.execute("SELECT holding_type, institution\
                                         FROM financial_holdings")
        htypes = {record[0] for record in response}
        inst = [record[-1] for record in response if record[-1] != None]
        if len(response) > 0:
            self.or_htypes.addItems(htypes)
            self.or_htypes.currentIndexChanged.connect(lambda: self._destination_options(htypes))
            # Create the institution combobox for both origin and destination:
            self.inst_cb_or = ComboBox(cwidget=self.centralwidget, 
                                       position=(self.or_htypes.x() + 150, self.or_htypes.y()),
                                       options=inst)
            self.inst_cb_des = ComboBox(cwidget=self.centralwidget,
                                        position=(self.dest_htypes.x() + 150, self.dest_htypes.y()),
                                        options=inst)
            # Hide them (Only apply when it's selected the "Card" htype)
            self.inst_cb_or.hide()
            self.inst_cb_des.hide()


    def _destination_options(self, htypes: list):
        """
        According to the selected holding type for the origin, 
        it's assigned the values that can be stored for destination. 
        """
        self.dest_htypes.clear()
        if self.or_htypes.currentText() == "Cash":
            self.inst_cb_or.hide()
            self.dest_htypes.addItems([htype for htype in htypes if htype != "Cash"])
        elif self.or_htypes.currentText() == "Card":
            self.inst_cb_or.show()
            self.dest_htypes.addItems(htypes)
        elif self.or_htypes.currentText() == '':
            self.inst_cb_or.hide()
        self.dest_htypes.setCurrentIndex(-1)
        self.dest_htypes.currentIndexChanged.connect(self._inst_visibility)


    def _inst_visibility(self):
        """
        The institution combo box for destination will only be
        displayed if it was selected the card option.
        """
        if self.dest_htypes.currentText() == "Cash" or self.dest_htypes.currentText() == '':
            self.inst_cb_des.hide()
        elif self.dest_htypes.currentText() == "Card":
            self.inst_cb_des.show()


    def _perform_the_transfer(self):
        """
        Once it was selected the holding type for origin and destination,
        and the amount to transfer, the balances are updated.
        """
        origin_query = self._build_query(
            data=(self.or_htypes.currentText(), self.inst_cb_or.currentText()),
            transfer_type="Origin"
            )
        dest_query = self._build_query(
            data=(self.dest_htypes.currentText(), self.inst_cb_des.currentText()),
            transfer_type="Destination"
        )
        committed = self.db_conn.execute(commands=[origin_query, dest_query])
        if committed == "Ok":
            Message_Box(title="Transfer",
                        text="The transfer has been completed.",
                        icon="Information")
            self._clear_fields()

    
    def _build_query(self, data: tuple | str, transfer_type: str) -> str:
        """
        """
        sign = {"Origin": "-", "Destination": "+"}
        template_query = f"UPDATE financial_holdings\
                          SET amount = amount {sign[transfer_type]} {self.amount.text()}\
                          WHERE holding_type = "
        htype, inst = data
        if htype == "Cash":
            return template_query + f"'{htype}'"
        elif htype == "Card":
            return template_query + f"'{htype}' AND institution = '{inst}'"
    

    def _clear_fields(self):
        """
        Clear the content of the fields related to the origin, destination 
        and the amount to transfer
        """
        self.or_htypes.setCurrentIndex(-1)
        self.amount.clear()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = MoneyDistribution()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
