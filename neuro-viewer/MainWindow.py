from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap, QImage, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction, QMessageBox, QSlider, QCheckBox
from PyQt5.QtWidgets import QFontDialog, QColorDialog, QTextEdit, QFileDialog
from PyQt5.QtWidgets import QCheckBox, QProgressBar, QComboBox, QLabel, QStyleFactory, QLineEdit, QInputDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import matplotlib.pyplot as plt
from math import ceil
import time

def clip(val, l, h):
    return l if val < l else (h if val > h else val)

def set_font_size(ui_label, size):
    font =  ui_label.font()
    font.setPointSize(size)
    ui_label.setFont(font)

class SliceSlider:
    def __init__(self, workspace, ref_slider):
        self.workspace = workspace
        self.ui_slider = ref_slider

    def get(self):
        return self.ui_slider.value()

    def set_min(self, m):
        self.min = m
        self.ui_slider.setMinimum(m)

    def set_max(self, M):
        self.max = M
        self.ui_slider.setMaximum(M)

    def inc(self):
        new_val = clip(self.get() + 1, self.min, self.max)
        self.ui_slider.setValue(new_val)

    def dec(self):
        new_val = clip(self.get() - 1, self.min, self.max)
        self.ui_slider.setValue(new_val)

    def get_ui(self):
        return self.ui_slider

    def redraw_workspace(self):
        self.workspace.current_slide = self.get()
        self.workspace.redraw()

class MainWindow(QMainWindow):
    right_panel_width = 100

    def __init__(self, workspace):
        super(MainWindow, self).__init__()
        self.setMouseTracking(True)

        self.workspace = workspace
        self.grid_rows, self.grid_cols = self.workspace.grid_size

        self.global_slider = None
        self.direction_labels = []

        self.setGeometry(50, 50, 300 * self.grid_cols + 300, 350 * self.grid_rows)
        self.setWindowTitle('Patient {} - NeuroViewer'.format(workspace.get_patient_name()))
        self.setWindowIcon(QIcon('pic.png'))

        self.resize_handlers = []

        self.init_menu()
        self.init_right_panel()
        self.init_slices()
        self.show()
        self.workspace.loaded()
        self.label_directions(self.workspace.mode)

    def wheelEvent(self, event):
        numDegrees = event.angleDelta().y() / 8
        numSteps = numDegrees / 15
        event.accept()
        if numDegrees < 0:
            self.global_slider.dec()
        else:
            self.global_slider.inc()

    def init_menu(self):
        openFile = QAction('&Open File', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.file_open)

        saveFile = QAction('&Save File', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.file_save)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

    def file_open(self):
        # need to make name an tuple otherwise i had an error and app crashed
        name, _ = QFileDialog.getOpenFileName(self, 'Open File', options=QFileDialog.DontUseNativeDialog)
        file = open(name, 'r')
        with file:
            pass

    def file_save(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', options=QFileDialog.DontUseNativeDialog)
        # file = open(name, 'w')

    def label_directions(self, mode):
        def label_slots(left_label, right_label):
            for pointers in self.direction_labels:
                pointers[0].setText(left_label)
                pointers[1].setText(right_label)
        def label_slider(top_label, bottom_label):
            self.slider_label_top.setText(top_label)
            self.slider_label_bottom.setText(bottom_label)
        _, plane = mode.split(':')
        if plane == 'x':
            label_slots('P', 'A')
            label_slider('R', 'L')
        if plane == 'y':
            label_slots('R', 'L')
            label_slider('A', 'P')
        if plane == 'z':
            label_slots('R', 'L')
            label_slider('I', 'S')

    def init_global_slider(self):
        self.global_slider = SliceSlider(self.workspace, QSlider(self))
        self.global_slider.set_min(0)
        self.global_slider.set_max(self.workspace.slider_size - 1)
        slider = self.global_slider.get_ui()
        slider.setValue(40)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(5)
        slider.valueChanged.connect(self.change_global_slide)
        self.slider_label_top = QLabel(self)
        set_font_size(self.slider_label_top, 13)
        self.slider_label_bottom = QLabel(self)
        set_font_size(self.slider_label_bottom, 13)

    def init_right_panel(self):
        allow_glass = False
        if allow_glass:
            modes_map = {0: 's:y', 1: 's:x', 2: 's:z', 3: 'g:y', 4: 'g:x', 5: 'g:z'}
        else:
            modes_map = {0: 's:y', 1: 's:x', 2: 's:z'}  # coronar / sagital / transverse
        mode_index = [key for key, value in modes_map.items() if value == self.workspace.mode][0]

        self.view_mode = QComboBox(self)
        self.view_mode.addItem('Coronal')
        self.view_mode.addItem('Sagital')
        self.view_mode.addItem('Transverse')
        if allow_glass:
            self.view_mode.addItem('Glass coronal')
            self.view_mode.addItem('Glass sagital')
            self.view_mode.addItem('Glass transverse')
        self.view_mode.setCurrentIndex(mode_index)

        def change_mode(i):
            self.workspace.mode = modes_map[i]
            self.workspace.redraw()
            self.label_directions(self.workspace.mode)
        self.view_mode.currentIndexChanged.connect(change_mode)

        self.show_colorbar = QCheckBox("Show colorbar", self)
        self.show_colorbar.setChecked(False)

        def change_colorbar():
            self.workspace.show_colorbar = self.show_colorbar.isChecked()
            self.workspace.redraw()
        self.show_colorbar.stateChanged.connect(change_colorbar)

        self.init_global_slider()

        self.pos_label = QLabel(self)
        self.pos_label.setAlignment(Qt.AlignLeft)
        self.pos_label.setText('Position')
        self.val_label = QLabel(self)
        self.val_label.setAlignment(Qt.AlignLeft)
        self.val_label.setText('Value')
        self.workspace.val_label = self.val_label

        def resize():
            left_edge = self.get_window_size()[0]-self.right_panel_width
            self.view_mode.move(left_edge, 50)
            self.view_mode.resize(80, 30)
            self.show_colorbar.move(left_edge, 80)
            self.show_colorbar.resize(80, 30)
            self.global_slider.get_ui().move(left_edge, 140)
            self.global_slider.get_ui().resize(50, 300)
            self.slider_label_top.move(left_edge + 12, 110)
            self.slider_label_bottom.move(left_edge + 12, 140 + 295)
            self.pos_label.move(left_edge, 500)
            self.pos_label.resize(90, 15)
            self.val_label.move(left_edge, 515)
            self.pos_label.resize(90, 15)
        resize()
        self.resize_handlers.append(resize)

    def init_slice(self, slot):
        slider_ticks = 200
        label_format = 'v={0:.3f}'
        thres_coef = slider_ticks / slot.max

        figure = plt.figure()
        canvas = FigureCanvas(figure)
        canvas.setParent(self)
        figure.set_facecolor('black')

        # nazev metody
        lname = QLabel(self)
        lname.setAlignment(Qt.AlignLeft)
        lname.setText(slot.name)
        lname.setStyleSheet('QLabel { background-color : black; color : white; }')
        lname.resize(120, 25)
        set_font_size(lname, 12)
        # font.setBold(True)

        # procentualni pokryti
        cname = QLabel(self)
        cname.setAlignment(Qt.AlignLeft)
        cname.setText('20 %')
        cname.setStyleSheet('QLabel { background-color : black; color : white; }')
        cname.resize(50, 25)
        set_font_size(cname, 12)

        # smer (R/L, A/P, I/S)
        def create_direction_label():
            dname = QLabel(self)
            dname.setAlignment(Qt.AlignLeft)
            dname.setStyleSheet('QLabel { background-color : black; color : white; }')
            dname.resize(10, 15)
            set_font_size(dname, 10)
            return dname
        dlname = create_direction_label()
        drname = create_direction_label()

        label = QLabel(self)
        label.setAlignment(Qt.AlignLeft)
        label.setText(label_format.format(slot.thres))

        # threshold slider
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(1)
        slider.setMaximum(slider_ticks)
        slider.setTickPosition(QSlider.TicksAbove)
        slider.setTickInterval(5)
        slider.setValue(int(round(slot.thres * thres_coef)))
        # slider.setFocusPolicy(Qt.NoFocus)

        # +/- checkboxes
        checkbox_plus = QCheckBox('+', self)
        checkbox_plus.setChecked(True)
        checkbox_minus = QCheckBox('-', self)
        checkbox_minus.setChecked(True)

        def change_tresh():
            show_plus = checkbox_plus.isChecked()
            show_minus = checkbox_minus.isChecked()
            thres_value = slider.value() / thres_coef
            label.setText(label_format.format(thres_value))
            slot.scale(thres_value, show_plus, show_minus)

        def resize():
            pos, size = self.calc_slots_size(slot.pos)
            pos = pos[0] + 1, pos[1] + 1
            canvas.move(*pos)
            canvas_size = size[0] - 1, size[1] - 18
            canvas.resize(*canvas_size)
            label.move(pos[0] + 5, pos[1] + canvas_size[1] + 1)
            label.resize(90, 15)
            lname.move(pos[0] + 15, pos[1] + 10)
            cname.move(pos[0] + 15, pos[1] + size[1] - 45)
            dlname.move(pos[0] + 15, int(pos[1] + ceil(size[1] / 2) - 20))
            drname.move(pos[0] + size[0] - 30, int(pos[1] + ceil(size[1] / 2) - 20))
            slider.move(pos[0] + 55, pos[1] + canvas_size[1] + 1)
            slider.resize(size[0] - 55 - 60 - 10, 15)
            checkbox_plus.move(int(round(pos[0] + size[0] - 60)), int(round(pos[1] + canvas_size[1] - 6)))
            checkbox_minus.move(int(round(pos[0] + size[0] - 30)), int(round(pos[1] + canvas_size[1] - 6)))
        resize()
        self.resize_handlers.append(resize)

        slider.valueChanged.connect(change_tresh)
        checkbox_plus.stateChanged.connect(change_tresh)
        checkbox_minus.stateChanged.connect(change_tresh)
        slot.set_gui(figure, canvas, cname)
        self.direction_labels.append((dlname, drname))

        def onmove(event):
            if event.xdata is not None:
                self.pos_label.setText('{0:.2f} x {0:.2f}'.format(event.xdata, event.ydata))
            else:
                self.pos_label.setText('Position')
            slot.mouse_move(event)

        canvas.mpl_connect('motion_notify_event', onmove)

    def init_slices(self):
        for slot in self.workspace.slots:
            self.init_slice(slot)
        self.change_global_slide()

    def calc_slots_size(self, pos):
        slots_width, slots_height = self.get_window_size()
        slots_width -= self.right_panel_width
        slots_height -= 10  # prostor pro status bar, slidery prilepene na spodni okraj se blbe ovladaly
        width, height = ceil(slots_width/self.grid_cols), ceil(slots_height/self.grid_rows)
        return ((pos[0]-1)*width, (pos[1]-1)*height + 20), (width, height)

    def change_global_slide(self):
        self.workspace.current_slide = self.global_slider.get()
        self.workspace.redraw()

    def question_example(self):
        choice = QMessageBox.question(self, 'Message', 'Are you sure to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            print('quit application')
        else:
            pass

    def get_window_size(self):
        return self.frameGeometry().width(), self.frameGeometry().height() - 60

    def resizeEvent(self, event):
        for fcn_resize in self.resize_handlers:
            fcn_resize()
        # self.workspace.redraw()

    # def keyPressEvent(self, event):
    #     pressedkey = event.key()
    #     if pressedkey == Qt.Key_Left:
    #         print('sipka <-')
    #     elif pressedkey == Qt.Key_Right:
    #         print('sipka ->')
    #     else:
    #         event.ignore()

