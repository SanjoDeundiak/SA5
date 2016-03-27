# coding=utf-8
import sys

import lab5
import classification as clsf

from PyQt4 import QtGui
from PyQt4.QtCore import QObject, SIGNAL, SLOT, pyqtSignal, pyqtSlot, Qt

app = QtGui.QApplication(sys.argv)
app.setApplicationName("Lab5_SA")

situation = [0]
factor = [0]
magic = [0.0]


class MainWindow(QtGui.QMainWindow):
    def __init__(self, cols, rows, parent=None):
        super(MainWindow, self).__init__(parent)
        self.cols = cols
        self.rows = rows

        self.eta_min = 0.1

        self.setGeometry(100, 100, 100 * self.cols + 35, 350)
        # self.setWindowState(Qt.WindowFullScreen)
        self.table_widget = TableWidget(self.rows, self.cols, self)
        self.table_widget.setGeometry(0, 0, 500, 40)
        self.result_widget = ResultsWidget(4, self)
        self.result_widget.setGeometry(0, 37.5 * 4 + 50, 700, 200)
        self.graph_buttons = GraphButtonsWidget(self)
        # self.graph_buttons.setGeometry(500, 37.5 * 4 + 50, 200, 200)
        self.graph_buttons.setGeometry(500, 0, 120, 40)

        self.labels = []

        self.own = False
        QObject.connect(self.table_widget.own, SIGNAL('stateChanged(int)'),
                        self, SLOT('change_own()'))

        self.current_row = 0
        self.current_col = 0
        QObject.connect(self.table_widget.table, SIGNAL('cellClicked(int,int)'),
                        self, SLOT('row_col_changed(int,int)'))

        QObject.connect(self.graph_buttons.inf_button, SIGNAL('clicked()'),
                        self, SLOT('inf_clicked()'))

        self.value_of_tolerance = 0.9
        QObject.connect(self.table_widget.start_button, SIGNAL('clicked()'),
                        self, SLOT('start_button_clicked()'))

        QObject.connect(self.table_widget.value_of_tolerance_combo_box, SIGNAL('currentIndexChanged(QString)'),
                        self, SLOT('value_of_tolerance_changed()'))

        # self.n_factor = 0
        # QObject.connect(self.graph_buttons.factor_edit, SIGNAL('textChanged(QString)'),
        #                 self, SLOT('n_factor_changed(QString)'))
        #
        # self.n_situation = 0
        # QObject.connect(self.graph_buttons.situation_edit, SIGNAL('textChanged(QString)'),
        #                 self, SLOT('n_situation_changed(QString)'))

        self.alpha = lab5.np.zeros((lab5.s_number, lab5.f_number))
        self.betta = lab5.np.zeros((lab5.s_number, lab5.f_number))
        self.gamma = lab5.np.zeros((lab5.s_number, lab5.f_number))

        self.alpha_own = lab5.np.zeros((lab5.s_number, lab5.f_number))
        self.betta_own = lab5.np.zeros((lab5.s_number, lab5.f_number))
        self.gamma_own = lab5.np.zeros((lab5.s_number, lab5.f_number))

    @pyqtSlot()
    def change_own(self):
        if not self.own:
            self.own = True
            lab5.const_own(self.alpha_own, self.betta_own, self.gamma_own)
        else:
            self.own = False
            lab5.const_variant(self.alpha, self.betta, self.gamma)

    @pyqtSlot("int", "int")
    def row_col_changed(self, row, col):
        self.current_row, self.current_col = row, col

    @pyqtSlot()
    def inf_clicked(self):
        if self.own:
            lab5.inf_plot_own(self.current_row, self.current_col)
        else:
            lab5.inf_plot(self.current_row, self.current_col)

    # @pyqtSlot("QString")
    # def n_factor_changed(self, value):
    #     self.n_factor = int(value)
    #
    # @pyqtSlot("QString")
    # def n_situation_changed(self, value):
    #     self.n_situation = int(value)

    @pyqtSlot()
    def value_of_tolerance_changed(self):
        self.value_of_tolerance = float(self.table_widget.value_of_tolerance_combo_box.currentText())

    @pyqtSlot()
    def start_button_clicked(self):
        for row in xrange(self.rows):
            for col in xrange(self.cols):
                if self.own:
                    res = lab5.solve_own(self.eta_min, self.value_of_tolerance, row, col)
                else:
                    res = lab5.solve(self.eta_min, self.value_of_tolerance, row, col)
                if not res:
                    self.table_widget.table.setItem(row, col, QtGui.QTableWidgetItem(""))
                else:
                    item = QtGui.QTableWidgetItem(str(res[0][0])[:6] + ":" + str(res[0][1])[:6])
                    self.table_widget.table.setItem(row, col, item)

        t_s = lab5.np.ndarray(shape=(self.rows, 2))
        for i in range(self.rows):
            if not self.own:
                t_s[i] = lab5.getT(i, self.value_of_tolerance)
            else:
                t_s[i] = lab5.getT_own(i, self.value_of_tolerance)
        t_s_transposed = t_s.transpose()

        res = clsf.classify(t_s_transposed[0], t_s_transposed[1])
        # self.result_widget.update_labels(res)
        self.labels = res
        for i in xrange(self.rows):
            self.result_widget.labels[i].setText(self.labels[i])
        print self.labels


class TableWidget(QtGui.QWidget):
    def __init__(self, rows, columns, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.own = QtGui.QCheckBox(u"Собственная функция", self)
        self.own.setGeometry(0, 0, 150, 40)

        self.value_of_tolerance_label = QtGui.QLabel(u"Величина допуска", self)
        self.value_of_tolerance_label.setGeometry(200, 0, 100, 40)

        self.value_of_tolerance_combo_box = QtGui.QComboBox(self)
        self.value_of_tolerance_combo_box.addItems(["0.5", "0.6", "0.7", "0.8", "0.9"])
        self.value_of_tolerance_combo_box.setCurrentIndex(4)
        self.value_of_tolerance_combo_box.setGeometry(300, 0, 40, 40)

        self.start_button = QtGui.QPushButton(u"Запуск", self)
        self.start_button.setGeometry(400, 0, 50, 40)

        self.table = QtGui.QTableWidget(rows, columns, parent)
        self.table.setCurrentCell(0, 0)
        vertical_headers = ["S" + str(i) for i in xrange(1, rows + 1)]
        self.table.setVerticalHeaderLabels(vertical_headers)
        horizontal_headers = [u"Ф" + str(i) for i in xrange(1, columns + 1)]
        self.table.setHorizontalHeaderLabels(horizontal_headers)
        self.table.setGeometry(0, 40, 100 * columns + 35, 37.5 * rows)


class ResultsWidget(QtGui.QWidget):
    def __init__(self, n_situations, parent=None):
        QtGui.QWidget.__init__(self, parent)
        # self.setGeometry(0, 0, 200, 100)
        self.n_situations = n_situations

        self.names = [u""] * self.n_situations

        # self.names = [u"Результати досліджень:", u""]
        # for i in xrange(n_situations):
        #     self.names.append(u"для ситуації S%(number)d" % {"number": i + 1})
        #     self.names.append(u"")

        self.result_label = QtGui.QLabel(u"Результаты исследования:", self)
        self.result_label.setGeometry(0, 0, 150, 20)

        self.labels = [QtGui.QLabel(self.names[i], self) for i in xrange(self.n_situations)]
        for i in xrange(n_situations):
            self.labels[i].setWordWrap(True)
            self.labels[i].setGeometry(0, 20 * (i + 2), 700, 20)

    def update_labels(self, names):
        for i in xrange(self.n_situations):
            self.names[i] = names[i]
            self.labels[i].setText(names[i])


        # self.grid = QtGui.QGridLayout()
        # self.grid.setSpacing(5)
        # self.pos = [(0, 0), (0, 1)]
        # for i in xrange(1, n_situations + 1):
        #     self.pos.append((i, 0))
        #     self.pos.append((i, 1))
        #
        # self.labels = []
        # for i in xrange(1 + n_situations):
        #     if i == 0:
        #         self.labels.append(QtGui.QLabel(self.names[i]))
        #     else:
        #         self.labels.append([QtGui.QLabel(self.names[2 * i - 1]), QtGui.QLabel(self.names[2 * i])])
        #
        # labels_to_update_grid = [self.labels[i][1].text() for i in xrange(1, 1 + self.n_situations)]
        # self.update_grid(labels_to_update_grid)
        # self.resize(500, 200)

    # def update_names(self, names):
    #     for i in xrange(1, 1 + self.n_situations):
    #         self.names[2 * i] = names[i - 1]
    #
    # def update_labels(self, names):
    #     self.update_names(names)
    #     for i in xrange(1, 1 + self.n_situations):
    #         self.labels[i][1].setText(self.names[i - 1])
    #
    # def update_grid(self, names):
    #     self.update_labels(names)
    #     # for i in reversed(xrange(self.grid.count())):
    #     #     widget_to_remove = self.grid.itemAt(i).widget()
    #     #     self.grid.removeWidget(widget_to_remove)
    #     #     widget_to_remove.setParent(None)
    #         # self.grid.itemAt(i).widget().deleteLater()
    #     for i in xrange(1 + self.n_situations):
    #         if i == 0:
    #             self.grid.addWidget(self.labels[0], self.pos[i][0], self.pos[i][1])
    #         else:
    #             self.grid.addWidget(self.labels[i][0], self.pos[2 * i][0], self.pos[2 * i][1])
    #             self.grid.addWidget(self.labels[i][1], self.pos[2 * i + 1][0], self.pos[2 * i + 1][1])
    #     self.setLayout(self.grid)


class GraphButtonsWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # self.factor_label = QtGui.QLabel(u"Фактор №", self)
        # self.factor_label.setGeometry(0, 0, 70, 20)
        # self.factor_edit = QtGui.QLineEdit(self)
        # self.factor_edit.setText("0")
        # self.factor_edit.setGeometry(70, 0, 20, 20)
        #
        # self.situation_label = QtGui.QLabel(u"Ситуація №", self)
        # self.situation_label.setGeometry(0, 30, 70, 20)
        # self.situation_edit = QtGui.QLineEdit(self)
        # self.situation_edit.setText("0")
        # self.situation_edit.setGeometry(70, 30, 20, 20)

        self.inf_button = QtGui.QPushButton(u"Показать графики", self)
        self.inf_button.setGeometry(0, 0, 120, 40)


form = MainWindow(7, 4)
form.setWindowTitle("System Analysis - Lab 5")
form.show()
QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))
sys.exit(app.exec_())
