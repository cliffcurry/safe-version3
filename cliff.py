import time

current_milli_time = lambda: int(round(time.time() * 1000))


from time import sleep

import sys

from PyQt5 import Qt
from PyQt5 import QtWidgets, QtCore , QtGui
from builtins import str
import string

class Window(Qt.QWidget):
 
     def __init__(self, parent = None):
         Qt.QWidget.__init__(self, parent)
         self.label = Qt.QLabel()
         formLayout = Qt.QFormLayout()
         layout = Qt.QGridLayout()
         layout.addWidget(self.label, 0, 0, 1, 3, QtCore.Qt.AlignCenter)
         self.setLayout(layout)
         #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
         #self.updateImage()
     def updateImage(self, text):
         font = Qt.QFont(self.label.font())
         font.setPointSizeF(50)
         metrics = Qt.QFontMetricsF(font)
         #text = str(self.tr('Swipe your card'))
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
         self.show()
    
 
if __name__ == "__main__":
 
     app = Qt.QApplication(sys.argv)
     window = Window()
     window.maximized=True
     window.updateImage('Swipe your Card')
     window.show()
     time.sleep(4)
     window.updateImage('Cliff Curry')
     time.sleep(4)
     window.updateImage('Access granted')
     time.sleep(4)
     window.updateImage('Access denied')
     sys.exit(app.exec_())