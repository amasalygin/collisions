from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPointF

from appwindow import Ui_AppWindow
from objects import ObjectsFabric, Objects
from map import map
import sys
import random

from relations import RelationsOverlay

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_AppWindow()
        self.ui.setupUi(self)
        self.overlay = RelationsOverlay(self)
        self.overlay.show()

    # по двойному нажатию создаем прямоугольник
    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            localPos = self.mapFromGlobal(e.globalPos())
            obj = ObjectsFabric.getObject(Objects.Rect, localPos.x(), localPos.y(), self.centralWidget())
            if obj is not None:
                if not map.rect_intersects(obj.geometry()):
                    obj.show()
                    obj.relation.startPaintRelation.connect(self.overlay.slotStartPaintRelation)
                    obj.relation.endPaintRelation.connect(self.overlay.slotEndPaintRelation)
                    obj.objectMoved.connect(self.overlay.update)
                    map.lockPoints(obj.geometry())
                else:
                    del obj

        QtWidgets.QWidget.mouseDoubleClickEvent(self, e)

    # передача в RelationOverlay текущей позиции мыши при движени
    def mouseMoveEvent(self, e):
        if self.overlay.isPaintRelation:
            self.overlay.mousePos = e.pos()
            self.overlay.update()

        QtWidgets.QWidget.mouseMoveEvent(self, e)

    # вместе с главным окном ресайзим карту координат объектов и RelationOverlay
    def resizeEvent(self, e):
        self.overlay.resize(self.size())
        map.resizeMap(self.size())
        QtWidgets.QWidget.resizeEvent(self,e)

    # по нажатию на линию связи - удаляем ее
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            localPos = QPointF(self.mapFromGlobal(e.globalPos()))
            rel = self.overlay.relationInPos(localPos)
            if rel is not None:
                self.overlay.deleteRelation(rel)



app = QtWidgets.QApplication([])
application = mywindow()
map.areaWidget = application
application.show()

for i in range(100):
    x = random.randint(0, application.width())
    y = random.randint(0, application.height())
    r = ObjectsFabric.getObject(Objects.Rect, x, y, application.centralWidget())
    if r is not None:
        if not map.rect_intersects(r.geometry()):
            r.show()
            r.relation.startPaintRelation.connect(application.overlay.slotStartPaintRelation)
            r.relation.endPaintRelation.connect(application.overlay.slotEndPaintRelation)
            r.objectMoved.connect(application.update)
            map.lockPoints(r.geometry())
        else:
            del r

sys.exit(app.exec())