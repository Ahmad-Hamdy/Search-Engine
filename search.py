from PyQt5 import QtCore, QtGui, QtWidgets, uic
from os import listdir, startfile

class signal_emitter(QtCore.QObject):
    search_result_signal = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot(str, str)
    def search(self, path, search_item):
        directories = listdir(path)
        if search_item.lower() in map(str.lower, directories):
            self.search_result_signal.emit(f'Perfect match "{search_item}"  in path: {path}')
        for directory in directories:
            if search_item.lower() in directory.lower() and search_item.lower() != directory.lower():
                #check if the string given is a part of the (file / folder)'s name
                self.search_result_signal.emit(f'Match "{directory}"  in path: {path}') 
            if "." not in directory:                # when checking for a folder
                try:
                    self.search(path + directory + "/" , search_item)
                except:
                    pass

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('search.ui', self)
        self.search_item = ""
        self.search_path = []
        self.results_height = 0
        self.setupUi()

    def setupUi(self):
        try:
            listdir('F:')
        except FileNotFoundError:
            self.F.hide()

        self.search_thread = signal_emitter()
        self.thread = QtCore.QThread(self)
        self.thread.start()
        self.search_thread.moveToThread(self.thread)

        self.results_layout = QtWidgets.QVBoxLayout();
        self.results_area.setLayout(self.results_layout);

        self.Search_entry.textChanged.connect(self.set_search_item)
        self.Search_entry.returnPressed.connect(self.get_results)
        self.Search_btn.clicked.connect(self.get_results)
        self.C.stateChanged.connect(lambda state: self.append_path(state, "C:/"))
        self.E.stateChanged.connect(lambda state: self.append_path(state, "E:/"))
        self.F.stateChanged.connect(lambda state: self.append_path(state, "F:/"))
        self.other.stateChanged.connect(self.other_checked)
        self.browse.clicked.connect(self.get_path)
        self.search_thread.search_result_signal.connect(lambda result: self.print_results(result))
        

    def get_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self)
        self.search_path.append(path)
        self.custom_path.setText(path)

    def set_search_item(self, item):

        self.search_item = item

    def other_checked(self, state):
        if (QtCore.Qt.Checked == state):
            self.custom_path.setEnabled(True)
            self.browse.setEnabled(True)
        else:
            self.custom_path.setEnabled(False)
            self.browse.setEnabled(False)

    def append_path(self, state, path):
        if (QtCore.Qt.Checked == state):
            self.search_path.append(path)
        else:
            self.search_path.remove(path)

    def get_results(self):
        if not self.Search_entry.text():
        	msg = QtWidgets.QMessageBox()
        	msg.setIcon(QtWidgets.QMessageBox.Critical)
        	msg.setWindowTitle("Error")
        	msg.setText("missing search item")
        	msg.setInformativeText("search bar in empty\nplease, provide a search item")
        	msg.exec_()
        	return

        if not self.search_path:
        	msg = QtWidgets.QMessageBox()
        	msg.setIcon(QtWidgets.QMessageBox.Critical)
        	msg.setWindowTitle("Error")
        	msg.setText("Path not provided")
        	msg.setInformativeText("No path selected\nPlease, select a path to search in")
        	msg.exec_()

        for path in self.search_path:
            try:
                QtCore.QMetaObject.invokeMethod(self.search_thread, "search",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, path),
                QtCore.Q_ARG(str, self.search_item))
            except Exception as e:
                print(e)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setWindowIcon(QtGui.QIcon("search.ico"))
                msg.setText("Path not valid")
                msg.setInformativeText("No path or Invalid path was provided\n please, provide a valid path and try again")
                msg.exec_()
                return
        
    def print_results(self, result):
        self.pushButton = QtWidgets.QPushButton(self.results_area)
        self.results_layout.addWidget(self.pushButton, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.pushButton.setText(result)
        if 'Perfect' in result:
            self.pushButton.setStyleSheet("color: rgb(0, 182, 0);")
        self.pushButton.setFlat(True)
        self.pushButton.clicked.connect(lambda :startfile(result[result.index(': ')+2:]))
        self.results_area.setMinimumHeight(self.results_height + 49)
        self.results_height += 49

    def closeEvent(self, event):
        self.search_path.clear()
        self.thread.terminate()

if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Ui_MainWindow()
	window.show()
	sys.exit(app.exec_())