import time

current_milli_time = lambda: int(round(time.time() * 1000))

import sys

from PyQt5 import Qt
from PyQt5 import QtWidgets, QtCore , QtGui
from builtins import str

class Window(Qt.QWidget):
 
     def __init__(self, parent = None):
     
         Qt.QWidget.__init__(self, parent)
         
         self.label = Qt.QLabel()
         
         self.lineEdit = Qt.QLineEdit("ABCDE")
         self.fontComboBox = Qt.QFontComboBox()
         self.sizeSpinBox = Qt.QDoubleSpinBox()
         self.sizeSpinBox.setMinimum(1.0)
         self.sizeSpinBox.setValue(12.0)
         saveButton = Qt.QPushButton(self.tr("Save"))
         
         self.lineEdit.textChanged.connect(self.updateImage)
         self.fontComboBox.currentFontChanged.connect(self.updateImage)
         self.sizeSpinBox.valueChanged.connect(self.updateImage)
         saveButton.clicked.connect(self.saveImage)
         
         formLayout = Qt.QFormLayout()
         formLayout.addRow(self.tr("&Text:"), self.lineEdit)
         formLayout.addRow(self.tr("&Font:"), self.fontComboBox)
         formLayout.addRow(self.tr("Font &Size:"), self.sizeSpinBox)
         
         layout = Qt.QGridLayout()
         layout.addWidget(self.label, 0, 0, 1, 3, QtCore.Qt.AlignCenter)
         layout.addLayout(formLayout, 1, 0, 1, 3)
         layout.addWidget(saveButton, 2, 1)
         self.setLayout(layout)
         
         self.updateImage()
         self.setWindowTitle(self.tr("Paint Text"))
     
     def updateImage(self):
     
         font = Qt.QFont(self.fontComboBox.currentFont())
         font.setPointSizeF(self.sizeSpinBox.value())
         metrics = Qt.QFontMetricsF(font)
         
         text = str(self.lineEdit.text())
         if not text:
             return
         
         rect = metrics.boundingRect(text)
         position = -rect.topLeft()
         
         pixmap = Qt.QPixmap(rect.width(), rect.height())
         color = QtGui.QColor.fromRgb (255, 255, 255, 255)
         pixmap.fill(color)
         
         painter = Qt.QPainter()
         painter.begin(pixmap)
         painter.setFont(font)
         painter.drawText(position, text)
         painter.end()
         
         self.label.setPixmap(pixmap)
     
     def saveImage(self):
     
         formats = Qt.QImageWriter.supportedImageFormats()
         formats = map(lambda suffix: u"*."+str(suffix), formats)
         path = str(Qt.QFileDialog.getSaveFileName(self, self.tr("Save Image"),
             "", self.tr("Image Files (*.png *.jpg *.bmp)")))
         
         if path:
             print(path)
             #if not self.label.pixmap().save(path[1]):
             #    Qt.QMessageBox.warning(self, self.tr("Save Image"),
             #       self.tr("Failed to save file at the specified location."))
 
 
if __name__ == "__main__":
 
     app = Qt.QApplication(sys.argv)
     window = Window()
     window.show()
     sys.exit(app.exec_())