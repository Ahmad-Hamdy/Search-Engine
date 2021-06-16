from PyQt5 import QtCore, QtGui, QtWidgets, uic
from os import listdir


class signal_emitter(QtCore.QObject):
	search_result_signal = QtCore.pyqtSignal(str)

	def search(self, path, search_item):
	    directories = listdir(path)
	    if search_item in directories:
	        self.search_result_signal.emit(f'found perfect match for "{search_item}"  in path: {path}\n\n')
	    for directory in directories:
	        if search_item.lower() in directory.lower() and search_item != directory:
	            #check if the string given is a part of the (file / folder)'s name
	            self.search_result_signal.emit(f'found match for "{search_item}"  in path: {path}\n\n')

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

        self.Search_entry.textChanged.connect(self.set_search_item)
        self.Search_entry.returnPressed.connect(self.get_results)
        self.Search_btn.clicked.connect(self.get_results)
        self.C.stateChanged.connect(lambda state: self.append_path(state, "C:/"))
        self.E.stateChanged.connect(lambda state: self.append_path(state, "E:/"))
        self.F.stateChanged.connect(lambda state: self.append_path(state, "F:/"))
        self.other.stateChanged.connect(self.other_checked)
        self.browse.clicked.connect(self.get_path)
        self.search_thread.search_result_signal.connect(self.results_area.append)

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
        print(self.search_path)

    def get_results(self):
        self.results_area.clear()
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
                self.search_thread.search(path, self.search_item)
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
        
        if not self.results_area.toPlainText():
        	self.results_area.setText("\n\n\t\t\tNo results found for \"" + self.Search_entry.text() + '"')  

    def closeEvent(self, event):
        self.search_path.clear()
        self.thread.terminate()

if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Ui_MainWindow()
	window.show()
	sys.exit(app.exec_())