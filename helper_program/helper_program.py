import sys, time
from math import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QAction, qApp, QWidget
from PyQt5.QtGui import QIcon, QRegExpValidator
import pandas as pd
import os


import logging

CSS ={
	'QWidget':
	{
		'background-color': '#555555',
	},
	'QLabel#label':
	{
		'color': '#888888',
		'background-color': '#444444',
		'font-weight': 'bold',
	},
	'QLabel#label:active':
	{
		'color': '#1d90cd',
	},
	'QPushButton#button':
	{
		'color': '#888888',
		'background-color': '#444444',
		'font-weight': 'bold',
		'border': 'none',
		'padding': '5px',
	},
	'QPushButton#button:active':
	{
		'color': '#ffffff',
	},
	'QPushButton#button:hover':
	{
		'color': '#1d90cd',
	}
}

def dictToCSS(dictionnary):
	stylesheet = ""
	for item in dictionnary:
		stylesheet += item + "\n{\n"
		for attribute in dictionnary[item]:
			stylesheet += "  " + attribute + ": " + dictionnary[item][attribute] + ";\n"
		stylesheet += "}\n"
	return stylesheet

#Copy-past from https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
class QPlainTextEditLogger(logging.Handler):
	def __init__(self, parent):
		super().__init__()
		self.widget = QtWidgets.QPlainTextEdit(parent)
		self.widget.setReadOnly(True)

	def emit(self, record):
		msg = self.format(record)
		self.widget.appendPlainText(msg)

class Main(QtWidgets.QMainWindow):
	def __init__(self, parent):
		super().__init__()
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.setStyleSheet(dictToCSS(CSS))
		self.resize(857, 555)

		#You can't set a QLayout directly on the QMainWindow. You need to create
		# a QWidget and set it as the central widget on the QMainWindow and
		#assign the QLayout to that. https://stackoverflow.com/questions/37304684/qwidgetsetlayout-attempting-to-set-qlayout-on-mainwindow-which-already
		self.main_widget = QWidget(self)
		self.setCentralWidget(self.main_widget)

		self.setWindowTitle('Beach Bound Sports helper program')

		#Establish vertical layout for the whole screen
		self.big_vertical_layout = QtWidgets.QVBoxLayout()
		#self.big_vertical_layout.setObjectName("big_vertical_layout")
		self.functional_area_layout = QtWidgets.QHBoxLayout()
		self.functional_area_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
		#self.functional_area_layout.setObjectName("functional_area_layout")
		self.app_functions_vert_layout = QtWidgets.QVBoxLayout()
		self.app_functions_vert_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
		#self.app_functions_vert_layout.setObjectName("app_functions_vert_layout")

		self.dateTime = QtWidgets.QLabel()
		self.dateTime.setMinimumSize(QtCore.QSize(150, 30))
		self.dateTime.setMaximumSize(QtCore.QSize(150, 30))
		self.check_time_thread = QtCore.QTimer(self)
		self.check_time_thread.setInterval(500) #.5 seconds
		self.check_time_thread.timeout.connect(self.update_clock)
		#self.dateTime.setObjectName("dateTime")
		self.app_functions_vert_layout.addWidget(self.dateTime)

		self.asset_watch_label = QtWidgets.QLabel("Functions:")
		self.asset_watch_label.setMinimumSize(QtCore.QSize(0, 15))
		self.asset_watch_label.setMaximumSize(QtCore.QSize(150, 20))
		#self.asset_watch_label.setObjectName("asset_watch_label")
		self.app_functions_vert_layout.addWidget(self.asset_watch_label, 0, QtCore.Qt.AlignTop)

		self.condition_report = QtWidgets.QPushButton('Condition Report' )
		self.condition_report.setMinimumSize(QtCore.QSize(150, 10))
		self.condition_report.setMaximumSize(QtCore.QSize(150, 20))
		#self.condition_report.setObjectName("condition_report")
		self.app_functions_vert_layout.addWidget(self.condition_report)
		self.condition_report.clicked.connect(self.condition_tsv)

		self.function2 = QtWidgets.QPushButton('+ function' )
		self.function2.setMinimumSize(QtCore.QSize(150, 10))
		self.function2.setMaximumSize(QtCore.QSize(150, 20))
		#self.function2.setObjectName("function2")
		self.app_functions_vert_layout.addWidget(self.function2)

		self.function3 = QtWidgets.QPushButton('+ function' )
		self.function3.setMinimumSize(QtCore.QSize(150, 10))
		self.function3.setMaximumSize(QtCore.QSize(150, 20))
		#self.function3.setObjectName("function3")
		self.app_functions_vert_layout.addWidget(self.function3)

		self.function4 = QtWidgets.QPushButton('+ function' )
		self.function4.setMinimumSize(QtCore.QSize(150, 10))
		self.function4.setMaximumSize(QtCore.QSize(150, 20))
		#self.function4.setObjectName("pushButton")
		self.app_functions_vert_layout.addWidget(self.function4)

		spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.app_functions_vert_layout.addItem(spacerItem)
		self.functional_area_layout.addLayout(self.app_functions_vert_layout)

		#Setup right side of the UI to handle money counting
		self.right_side_layout=QtWidgets.QVBoxLayout()
		self.money_count_label=QtWidgets.QLabel("Cash conversion mini app: ")
		self.money_count_label.setObjectName("right_side_label")

		self.ccw_row1 = QtWidgets.QHBoxLayout()
		#https://python-forum.io/thread-23451.html
		#Validate that only floats are entered into text fields using Regex
		float_only = QRegExpValidator(QRegExp(r'[0-9].+'))
		self.tender_label=QtWidgets.QLabel("Supplied Tender by Customer: ")
		self.tender_field=QtWidgets.QDoubleSpinBox(self)
		#self.tender_field.setValidator(float_only)
		self.ccw_row1.addWidget(self.tender_label)
		self.ccw_row1.addWidget(self.tender_field)

		self.ccw_row2 = QtWidgets.QHBoxLayout()
		self.amnt_due_label=QtWidgets.QLabel("Amount Due from Customer: ")
		self.amnt_due_field=QtWidgets.QDoubleSpinBox(self)
		#self.amnt_due_field.setValidator(float_only)
		self.ccw_row2.addWidget(self.amnt_due_label)
		self.ccw_row2.addWidget(self.amnt_due_field)

		####################################
		# Link to function when value changes
		self.amnt_due_field.valueChanged.connect(self.refresh)
		####################################
		####################################
		# Link to function when value changes
		self.tender_field.valueChanged.connect(self.refresh)
		####################################



		self.ccw_row2half=QtWidgets.QHBoxLayout()
		self.change_due_label=QtWidgets.QLabel("Change back, least items: ")
		self.change_due=QtWidgets.QDoubleSpinBox()
		self.change_due.setReadOnly(True)
		self.ccw_row2half.addWidget(self.change_due_label)
		self.ccw_row2half.addWidget(self.change_due)
		#First proposal on change back, least currency items back
		self.ccw_row3=QtWidgets.QHBoxLayout()
		self.fifty_label=QtWidgets.QLabel('50s:')
		self.fiftys=QtWidgets.QSpinBox()
		self.fiftys.setReadOnly(True)
		self.twenties_label=QtWidgets.QLabel('20s:')
		self.twenties=QtWidgets.QSpinBox()
		self.twenties.setReadOnly(True)
		self.tens_label=QtWidgets.QLabel('10s:')
		self.tens=QtWidgets.QSpinBox()
		self.tens.setReadOnly(True)
		self.fives_label=QtWidgets.QLabel('5s:')
		self.fives=QtWidgets.QSpinBox()
		self.fives.setReadOnly(True)
		self.ones_label=QtWidgets.QLabel('1s:')
		self.ones=QtWidgets.QSpinBox()
		self.ones.setReadOnly(True)
		temp_list = [self.fifty_label, self.fiftys, self.twenties_label, self.twenties, self.tens_label, self.tens, self.fives_label, self.fives, self.ones_label, self.ones]
		[self.ccw_row3.addWidget(x) for x in temp_list]

		self.ccw_row4=QtWidgets.QHBoxLayout()
		self.quarters_label=QtWidgets.QLabel('.25s:')
		self.quarters=QtWidgets.QSpinBox()
		self.quarters.setReadOnly(True)
		self.dimes_label=QtWidgets.QLabel('.10s:')
		self.dimes=QtWidgets.QSpinBox()
		self.dimes.setReadOnly(True)
		self.nickles_label=QtWidgets.QLabel('.05s:')
		self.nickles=QtWidgets.QSpinBox()
		self.nickles.setReadOnly(True)
		self.pennies_label=QtWidgets.QLabel('.01s:')
		self.pennies=QtWidgets.QSpinBox()
		self.pennies.setReadOnly(True)
		temp_list = [self.quarters_label, self.quarters, self.dimes_label, self.dimes, self.nickles_label, self.nickles, self.pennies_label, self.pennies]
		[self.ccw_row4.addWidget(x) for x in temp_list]



		spacer_item2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

		#add all my Widgets to right_side_layout VBox
		self.right_side_layout.addWidget(self.money_count_label)
		self.right_side_layout.addLayout(self.ccw_row1)
		self.right_side_layout.addLayout(self.ccw_row2)
		self.right_side_layout.addLayout(self.ccw_row2half)
		self.right_side_layout.addLayout(self.ccw_row3)
		self.right_side_layout.addLayout(self.ccw_row4)
		self.right_side_layout.addItem(spacer_item2)



		self.functional_area_layout.addLayout(self.right_side_layout)
		self.functional_area_layout.setStretch(0, 0)
		self.big_vertical_layout.addLayout(self.functional_area_layout)

		#Console log and options grid setup
		self.console_log = QPlainTextEditLogger(self)
		self.console_log.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
		#https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
		logging.getLogger().addHandler(self.console_log)
		self.console_log.widget.setMaximumSize(QtCore.QSize(16777215, 50))
		#self.console_log.setObjectName("console_log")
		#You must add the object>.widget< to allow custom objects to add to layout
		self.big_vertical_layout.addWidget(self.console_log.widget)
		self.options_grid = QtWidgets.QGridLayout()
		self.options_grid.setObjectName("options_grid")


		# Set the window's main layout
		self.main_widget.setLayout(self.big_vertical_layout)

		#File menu actions
		exitAct = QAction(QIcon('exit.png'), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)
		#initialize statusbar and menubar
		self.statusBar()
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAct)

		self.menubar = self.menuBar()
		self.menubar.setGeometry(QtCore.QRect(0, 0, 857, 22))
		self.menubar.setObjectName("menubar")
		self.menuFile = QtWidgets.QMenu(self.menubar)
		self.menuFile.setObjectName("menuFile")
		self.menuAnalysis = QtWidgets.QMenu(self.menubar)
		self.menuAnalysis.setObjectName("menuAnalysis")
		self.menuHelp = QtWidgets.QMenu(self.menubar)
		self.menuHelp.setObjectName("menuHelp")
		self.setMenuBar(self.menubar)

		self.actionExit = QtWidgets.QAction(self)
		self.actionExit.setObjectName("actionExit")
		self.menuFile.addAction(self.actionExit)
		self.menubar.addAction(self.menuFile.menuAction())
		self.menubar.addAction(self.menuAnalysis.menuAction())
		self.menubar.addAction(self.menuHelp.menuAction())


		self.show()


	##########################################
	# Function for refreshing the output label
	def refresh(self):
		tender = self.tender_field.value()
		due = self.amnt_due_field.value()
		change = tender - due
		self.change_due.setValue(change)
		fifties=0;twenties=0;tens=0;fives=0;ones=0;quarters=0;dimes=0;nickles=0;pennies=0

		if (floor(change/50)>0):
			fifties=floor(change/50)
			change=change-fifties*50
		if (floor(change/20)>0):
			twenties=floor(change/20)
			change=change-twenties*20
		if (floor(change/10)>0):
			tens=floor(change/10)
			change=change-tens*10
		if (floor(change/5)>0):
			fives=floor(change/5)
			change=change-fives*5
		if (floor(change)>0):
			ones=floor(change)
			change=change-ones
		##################################
		#powergap for floatingpoint errors
		##################################
		big_change = int(int(round(change*1000))/10)
		if (floor(big_change/25)>0):
			quarters=floor(big_change/25)
			big_change=(big_change-quarters*25)
		if (floor(big_change/10)>0):
			dimes=floor(big_change/10)
			big_change=(big_change-dimes*10)
		if (floor(big_change/5)>0):
			nickles=floor(big_change/5)
			big_change=(big_change-nickles*5)
		if (big_change>0):
			pennies = big_change
			big_change = big_change-pennies*1

		self.fiftys.setValue(fifties); self.twenties.setValue(twenties); self.tens.setValue(tens)
		self.fives.setValue(fives); self.ones.setValue(ones); self.quarters.setValue(quarters)
		self.dimes.setValue(dimes); self.nickles.setValue(nickles);self.pennies.setValue(pennies)

		print(big_change)
		if (int(big_change)!=0):
			logging.info(str(change))

	##########################################

	def condition_tsv(self):
		fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','./',"txt files (*.txt *.csv)")
		with open(fname, 'r', encoding='utf-8') as file:

			df = pd.read_csv(file.name, delimiter="\t")

	def logger_test(self):
		logging.debug('debug')
		logging.info('info')
		logging.warning('Test')
		logging.error('successful')

	def update_clock(self):
		pass

if __name__== '__main__':
	app = QtWidgets.QApplication([])
	gui = Main(app)
	sys.exit(app.exec_())
