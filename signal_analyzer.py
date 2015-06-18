import sys, random, math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy
import pandas
import matplotlib as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: Signal Analyzer')
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
#        for testing only
#        self.display_test_data()
        self.pressed = False
        self.index = 0
        self.result=numpy.array([])
        
#    def display_test_data(self):
#        self.file_name = "15.06.10 cPDMS 1.5cm #1.xlsx"
#        if self.file_name:
#            self.data = pandas.read_excel(self.file_name)
#            # clear the axes and redraw the plot anew
#            self.axes.clear()        
#            self.data.plot(x='Time - Plot 0', 
#                           y='Amplitude - Plot 0',
#                           ax=self.axes)
#            self.canvas.draw()
#            self.spinbox.setRange(0, 10000)
#            self.statusBar().showMessage('Opened data file %s' % self.file_name, 2000)
            
    def open_data(self):
        file_formats = "*.xlsx"
        self.file_name = QFileDialog.getOpenFileName(self,
                                                     'Select data file',
                                                     file_formats)
        if self.file_name:
            self.data = pandas.read_excel(self.file_name)
            # clear the axes and redraw the plot anew
            self.axes.clear()        
            self.data.plot(x='Time - Plot 0', 
                      y='Amplitude - Plot 0',
                      ax=self.axes)
            self.canvas.draw()
            self.xmin, self.xmax = self.axes.get_xlim()
            self.ymin, self.ymax = self.axes.get_ylim()
            self.spinbox.setRange(0, self.xmax-self.xmin)
            self.statusBar().showMessage('Opened data file %s' % self.file_name, 2000)

    def save_plot(self):
        file_formats = "PNG (*.png)|*.png"
        
        path = QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_formats)
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """Electrical signal analyzer for piezoelectric device
    
        """
        QMessageBox.about(self, "About the demo", msg.strip())
        self.statusBar().showMessage('Opened data file %s' % self.file_name, 2000)
    
    def on_measure(self):
        if self.checkbox_measure.isChecked():
            # function evoked after checking left cursor
            self.rect = plt.patches.Rectangle((self.xmin, self.ymin),
                                              0.1*(self.xmax-self.xmin),
                                              self.ymax-self.ymin,
                                              facecolor='grey',
                                              alpha=0.3)
            self.axes.add_patch(self.rect)
            self.canvas.draw()
            self.statusBar().showMessage('Diaplaying measuring box')   
        else:
            self.rect.remove()
            self.canvas.draw()

    def on_spin(self):
        # function evoked after changing spinbox value
        self.rect.set_width(self.spinbox.value())
        self.canvas.draw()
        self.statusBar().showMessage('Diaplaying measuring box')   

    def button_press_callback(self, event):
        self.origin_x = event.xdata
        self.pressed = True
               
    def button_release_callback(self, event):
        self.pressed = False
        xmin = self.rect.get_x()
        xmax = self.rect.get_x()+self.rect.get_width()
        self.label_left_value.setText(str(xmin))
        self.label_right_value.setText(str(xmax))
        
        self.data_subset = self.data.ix[math.ceil(xmin):math.floor(xmax), 1]
        self.label_max_value.setText(str(max(self.data_subset)))
        self.label_min_value.setText(str(min(self.data_subset)))
        self.label_mean_value.setText(str(self.data_subset.mean()))
        
    def motion_notify_callback(self, event):
        if self.pressed:
            dx = event.xdata - self.origin_x
            self.rect.set_x(self.rect.get_x()+dx/5)
            self.canvas.draw()
    
    def on_write(self):
        self.table_result.setRowCount(self.index+1)
        self.table_result.setItem(self.index, 
                                  0, 
                                  QTableWidgetItem(str(self.index+1)))       
        self.table_result.setItem(self.index, 
                                  1, 
                                  QTableWidgetItem(str(self.data_subset.mean())))   
        self.result=numpy.append(self.result, 
                                 [self.index+1, self.data_subset.mean()])
        self.index=self.index+1
                
    def on_save(self):
        file_formats = "TXT (*.txt)|*.txt"
        
        path = QFileDialog.getSaveFileName(self, 
                        'Save results', '', 
                        file_formats)
        if path:
            self.result = self.result.reshape((-1, 2))
            numpy.savetxt(path, 
                          self.result, 
                          fmt='%.1f', 
                          delimiter=' ', 
                          header='Displacement Resistance', 
                          comments=''
                          )
        
    def create_main_frame(self):
        self.main_frame = QWidget()
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.axes = self.fig.add_subplot(111)
        self.canvas.mpl_connect('button_press_event', 
                                self.button_press_callback)
        self.canvas.mpl_connect('button_release_event', 
                                self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', 
                                self.motion_notify_callback)
        
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        grid.addWidget(self.mpl_toolbar, 0, 0, 1, 7)
        grid.addWidget(self.canvas, 1, 0, 1, 5)
        
        # talbe displaying measurement results
        self.table_result = QTableWidget()
        self.table_result.setColumnCount(2)     
        self.table_result.setHorizontalHeaderLabels(['Displacement', 'Resistance'])
        grid.addWidget(self.table_result, 1, 5, 1, 2)
        
        # check to show measuring box
        self.checkbox_measure = QCheckBox('Measuring box')
        grid.addWidget(self.checkbox_measure, 2, 0)
        self.connect(self.checkbox_measure, SIGNAL('stateChanged(int)'),
                     self.on_measure)
        
        # set measuring box width
        self.label_width = QLabel('Measuring box width:')
        grid.addWidget(self.label_width, 3, 0)
        self.spinbox = QDoubleSpinBox()
        grid.addWidget(self.spinbox, 4, 0)
        self.connect(self.spinbox, SIGNAL('valueChanged(double)'),
                     self.on_spin)
        
        # left cursor
        self.label_left = QLabel('Left position:')
        grid.addWidget(self.label_left, 2, 1)
        self.label_left_value = QLabel('N/A')
        grid.addWidget(self.label_left_value, 2, 2)
        
        # right cursor
        self.label_right = QLabel('Right position:')
        grid.addWidget(self.label_right, 3, 1)
        self.label_right_value = QLabel('N/A')
        grid.addWidget(self.label_right_value, 3, 2)
        
        self.label_max = QLabel('Maximum:')
        grid.addWidget(self.label_max, 2, 3)
        self.label_max_value = QLabel('N/A')
        grid.addWidget(self.label_max_value, 2, 4)
        self.label_min = QLabel('Mininum:')
        grid.addWidget(self.label_min, 3, 3)
        self.label_min_value = QLabel('N/A')
        grid.addWidget(self.label_min_value, 3, 4)
        self.label_mean = QLabel('Mean:')
        grid.addWidget(self.label_mean, 4, 3)
        self.label_mean_value = QLabel('N/A')
        grid.addWidget(self.label_mean_value, 4, 4)
        
        self.button_write = QPushButton("&Write")
        grid.addWidget(self.button_write, 2, 5)
        self.connect(self.button_write, SIGNAL('clicked()'), self.on_write)
        
        self.button_save = QPushButton("&Save")
        grid.addWidget(self.button_save, 2, 6)
        self.connect(self.button_save, SIGNAL('clicked()'), self.on_save)
        
        self.main_frame.setLayout(grid)
        self.setCentralWidget(self.main_frame)
        
    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        open_file_action = self.create_action("&Open data",
            shortcut="Ctrl+O", slot=self.open_data, 
            tip="Select the data file")
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (open_file_action, None, load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()