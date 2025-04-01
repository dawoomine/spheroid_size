import os

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QSpinBox, QDoubleSpinBox

from smi import SMI

class QTWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.label_filename = None
        self.label_output_dirname = None
        self.spinbox_scalebar_diameter = None
        self.dspinbox_ratio = None
        self.label_result_panel: QLabel = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label_filename = QLabel(None, self)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Image File:", self))
        hbox.addWidget(self.label_filename)
        layout.addLayout(hbox)

        btn_image = QPushButton("&Open", self)
        btn_image.clicked.connect(self.open_file_dialog)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_image)
        layout.addLayout(hbox)

        self.label_output_dirname = QLabel(None, self)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Output directory:", self))
        hbox.addWidget(self.label_output_dirname)
        layout.addLayout(hbox)

        btn_output = QPushButton("&Select", self)
        btn_output.clicked.connect(self.select_output_directory)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_output)
        layout.addLayout(hbox)

        self.spinbox_scalebar_diameter = QSpinBox()
        self.spinbox_scalebar_diameter.setMinimum(0)
        self.spinbox_scalebar_diameter.setMaximum(1000000)
        self.spinbox_scalebar_diameter.setSingleStep(1)
        self.spinbox_scalebar_diameter.setSuffix(" μM")
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Scalebar diameter: ", self))
        hbox.addWidget(self.spinbox_scalebar_diameter)
        layout.addLayout(hbox)

        self.dspinbox_ratio = QDoubleSpinBox()
        self.dspinbox_ratio.setRange(0, 100)
        self.dspinbox_ratio.setSingleStep(0.01)
        self.dspinbox_ratio.setDecimals(2)
        self.dspinbox_ratio.setValue(1.0)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Ratio:", self))
        hbox.addWidget(self.dspinbox_ratio)
        layout.addLayout(hbox)

        btn_measure = QPushButton("&Measure", self)
        btn_measure.clicked.connect(self.measure)
        btn_exit = QPushButton("Exit", self)
        btn_exit.clicked.connect(QCoreApplication.instance().quit)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_measure)
        hbox.addWidget(btn_exit)
        layout.addLayout(hbox)

        self.label_result_panel = QLabel("Result", self)
        hbox = QHBoxLayout()
        hbox.addWidget(self.label_result_panel)
        layout.addLayout(hbox)

        self.setLayout(layout)

        self.setWindowTitle("Spheroid Size Checker")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(300, 300, 400, 300)
        self.show()

    def open_file_dialog(self):
        filename = QFileDialog.getOpenFileName(self, 'Select image file', './')[0]
        if filename is not None and isinstance(filename, str) and len(filename):
            self.label_filename.setText(filename)
            self.label_output_dirname.setText(os.path.dirname(self.label_filename.text()))

    def select_output_directory(self):
        dirname = QFileDialog.getExistingDirectory(self)
        if dirname:
            self.label_output_dirname.setText(dirname)

    def measure(self):
        try:
            filename = self.label_filename.text()
            output_dirname = self.label_output_dirname.text()
            scalebar_diameter = self.spinbox_scalebar_diameter.value()
            ratio = self.dspinbox_ratio.value()

            smi = SMI(scalebar_diameter, ratio, output_dirname)
            smi.measure(filename)
            QMessageBox.information(self, None, "Done")
            result = "Result: \n" \
                     + f"contours: {smi.num_of_contours}\n" \
                     + f"ellipses: {smi.num_of_ellipses}\n" \
                     + f"diameter average: {smi.diameter_average}\n" \
                     + f"diameter standard deviation: {smi.diameter_standard_deviation}\n" \
                     + f"result image: {smi.result_image}\n" \
                     + f"result data: {smi.result_data}"
            self.label_result_panel.setText(result)
        except Exception as e:
            QMessageBox.critical(self, e.__class__.__name__, f"{e.__class__.__name__}: {e}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ex = QTWindow()
    app.exec_()
