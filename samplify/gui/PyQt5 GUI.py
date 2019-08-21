import sys

from PyQt4 import QtGui, QtCore


class MyGuiWindow(QtGui.QMainWindow):

    def __init__(self):

        # super inherits the class 'MyGuiWindow' with whichever classes are passed into it
        super(MyGuiWindow, self).__init__()

        """
            We will declare our initial parameters for our main window which will run at startup.
            
            We can change our windows later using other methods. But this will be our 'foundation' or presets for the
            class upon startup.
        """

        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle("PyQT Tuts")
        self.setWindowIcon(QtGui.QIcon('Samplify Logo.png'))

        # call our 'home' method to generate main window
        self.home()

    def home(self):
        """
                    **********STATUS BAR && DROP MENUS**********
        """

        self.statusBar()

        # declare a mutable menuBar as a new variable
        mainMenu = self.menuBar()

        # declare a new drop down menu column
        fileMenu = mainMenu.addMenu('&File')

        # create a new 'action' for the object we just created.
        extractAction = QtGui.QAction("&Quit", self)

        # statusTip allows dialogue description in the bottom left corner when hovering
        extractAction.setStatusTip("Leave The App")

        # we can set a shortcut/hotkey for the action
        extractAction.setShortcut("Ctrl+Q")

        # connect the trigger to the actionObject
        extractAction.triggered.connect(self.close_application)

        # add action to drop down menu
        fileMenu.addAction(extractAction)

        #
        # note: instead of re-declaring the changed object as the same name,
        # it is better practice to label your menu objects as they change.
        #
        # DON'T DO: mainMenu = mainMenu.addMenu('&something')
        #

        """
                        **********TOOLBARS**********
        """

        # create a new action
        newAction = QtGui.QAction("put text or (QIcon('')) here", self)

        # connect a trigger to the action
        newAction.triggered.connect(self.close_application)

        # create a toolbar object
        self.toolBar = self.addToolBar("Extraction")

        # add action to the toolbar
        self.toolBar.addAction(newAction)

        """
                        **********COMMON BUTTON OBJECTS**********
        """

        # create a new button object
        btn = QtGui.QPushButton("Quit", self)

        # move the button to position of the window
        btn.move(100, 100)

        # resize button, 'sizeHint()' will optimize size automatically
        btn.resize(btn.sizeHint())

        # when clicked, connect an action
        btn.clicked.connect(self.close_application)

        """
                    **********CHECK BOXES**********
        """

        # create our checkbox object
        checkBox = QtGui.QCheckBox('Enlarge Window', self)

        # move it out of the way so we can click without interference
        checkBox.move(200, 25)

        # resize optimally
        checkBox.sizeHint()

        # check for state change
        checkBox.stateChanged.connect(self.enlarge_window)

        """
                    **********PROGRESS BARS**********
        """

        # create a new progress bar object
        self.progressBar = QtGui.QProgressBar(self)

        # set dimensions/geometry
        self.progressBar.setGeometry(200, 80, 250, 20)

        # create a simple 'download' button
        self.btn = QtGui.QPushButton("Download", self)

        # move button to place to see
        self.btn.move(200, 120)

        # when btn is clicked, connect the download method
        self.btn.clicked.connect(self.download)

        """
                    **********STYLES**********
        """

        # print the current default OS style
        print(self.style().objectName())

        # create a new variable 'styleChoice', and assign a label
        self.styleChoice = QtGui.QLabel("Windows Vista", self)

        # create a new comboBox object
        comboBox = QtGui.QComboBox(self)

        # add all items from QStyleFactory class
        comboBox.addItems(QtGui.QStyleFactory.keys())

        # move the comboBox to a place where we can freely select it
        comboBox.move(50, 250)

        # do the same for styleChoice Label
        self.styleChoice.move(50, 150)

        # when comboBox is changed by user, connect from style_choice method
        comboBox.activated[str].connect(self.style_choice)

        """
                    **********FONT PICKER WIDGET**********
        """

        # In this example instead of naming a mutable object directly, we will create an
        # action and refer to a function containing the object. This will also allow us
        # to return the variables from the font picker widget.

        # create a new font picker action, give it a name
        fontChoice = QtGui.QAction('Font picker', self)

        # connect the fontChoice action with the trigger (a new function)
        fontChoice.triggered.connect(self.font_choice)

        # add the action to the toolBar
        self.toolBar.addAction(fontChoice)

        """
                        **********Color Picker Widget**********
        """

        # declare a object variable 'color'. This going to hold the 3 RGB values for our color picker
        color = QtGui.QColor(0,0,0)

        # declare an action variable so the user can open color picker widget from the toolbar
        fontColor = QtGui.QAction('Font bg Color', self)

        # connect the function that calls the widget
        fontColor.triggered.connect(self.color_picker)


        # add the action object to the toolbar so we can click and open the widget
        self.toolBar.addAction(fontColor)


        """
                        **********CALENDAR WIDGET**********
        """
        # declare our calendar widget and move to a position where we can click
        cal = QtGui.QCalendarWidget(self)
        cal.move(500,200)
        cal.resize(200,200)


        """
                        **********TEXT EDITOR WINDOW**********
        """

        # declare an action to check for event
        openEditor = QtGui.QAction("&Editor", self)

        # set a quick hotkey shortcut
        openEditor.setShortcut("Ctrl+E")

        # add a little statusTip for good practice
        openEditor.setStatusTip('Open Editor')

        # connect the text editor that we will create a function for later
        openEditor.triggered.connect(self.editor)

        # declare a new menu item for the editor
        editorMenu = mainMenu.addMenu("&Editor")

        # add action to the menu to open the editor event
        editorMenu.addAction(openEditor)

        """
                        **********FILE DIALOGUE BROWSER**********
        """

        # add a open file action/menu item to the menuBar
        openFile = QtGui.QAction("&Open File", self)
        openFile.setShortcut("Ctrl+F")
        openFile.setStatusTip("Open File Browser")
        openFile.triggered.connect(self.file_open)

        saveFile = QtGui.QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip("Save File...")
        saveFile.triggered.connect(self.file_save)

        # add a column to the menuBar
        fileMenu = mainMenu.addMenu('&File')

        # add the event to open the file to the menu
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        # show the app window
        self.show()


    def file_save(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name, 'w')
        text = self.textEdit.toPlainText()
        file.write(text)
        file.close()

    def file_open(self):
        # declare a file browser dialogue box that will return the name of the file (path)
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')

        # declare a  variable to open the path of the file
        file = open(name, 'r')

        # call the editor function so we can visually see whats being loaded, otherwise it's just stuck in memory
        self.editor()

        # use the 'file' variable to load the contents into the editor
        with file:
            text = file.read()
            self.textEdit.setText(text)


    def editor(self):
        # declare a text editor 'widget'
        self.textEdit = QtGui.QTextEdit()

        # add and 'takeover' to QMainWidow
        self.setCentralWidget(self.textEdit)


    def color_picker(self):
        # open a QColorDialog box and grab the selected color form the user input
        color = QtGui.QColorDialog.getColor()

        # set the background color of the styleChoice object by the returned name of the color variable
        self.styleChoice.setStyleSheet("QWidget { background-color: %s}" % color.name())


    def font_choice(self):
        # QtGui.QFontDialog.getFont() will return 2 variables-- font && valid
        font, valid = QtGui.QFontDialog.getFont()

        # if valid is met
        if valid:
            # we will change our previous 'styleChoice' object in this example
            self.styleChoice.setFont(font)

    def style_choice(self, text):
        # Grab the text from the Label
        self.styleChoice.setText(text)

        # Change the GUI application's style from selected label
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(text))

    def download(self):
        # declare a new integer variable
        self.completed = 0

        # increment until at 100
        while self.completed < 100:
            self.completed += 0.0001

            # increment the progressBar per iteration
            self.progressBar.setValue(self.completed)

    def enlarge_window(self, state):

        # check the boolean state of the checkbox
        if state == QtCore.Qt.Checked:
            self.setGeometry(50, 50, 1000, 600)
        else:
            self.setGeometry(50, 50, 500, 300)

    def close_application(self):

        """
                    **********MESSAGE BOXES**********
        """

        # create a new prompt
        newPrompt = QtGui.QMessageBox.question(self, 'This is the message box header!',
                                               "Do you really want to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        # make the conditional statement
        if newPrompt == QtGui.QMessageBox.Yes:
            print("quiting...")
            sys.exit()
        else:
            pass

        print("woahhhhh so custom!!!")
        sys.exit()


def run():

    # instantiate the GUI (this is what actually creates the main gui window object)
    appGui = QtGui.QApplication(sys.argv)

    # name & instantiate a new instance of MyGuiWindow() class
    GUI = MyGuiWindow()

    # cleanly close the application. this avoids auto-closing after program has been started.
    sys.exit(appGui.exec_())


run()