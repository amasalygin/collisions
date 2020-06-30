from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QObject, QPoint, QLine, pyqtSignal
from config import RP_SIZE, L_SIZE
from math import sqrt

# Класс реализующий программное представление связей между объектами
# Хранит в себе 2 связанных объекта, и QLine между ними
class Relation(QObject):
    def __init__(self, obj1: 'Object', obj2: 'Object', parent=None):
        super(Relation, self).__init__(parent=parent)
        self.__object1 = obj1
        self.__object2 = obj2

        self.__object1.relation.relatedTo.append(self.__object2)
        self.__object2.relation.relatedTo.append(self.__object1)

        self.line = QLine()
        self.calculateLine()

        self.__object1.objectMoved.connect(self.calculateLine)
        self.__object2.objectMoved.connect(self.calculateLine)

    def __del__(self):
        self.__object1.relation.relatedTo.remove(self.__object2)
        self.__object2.relation.relatedTo.remove(self.__object1)

    @property
    def object1(self):
        return self.__object1

    @property
    def object2(self):
        return self.__object2

    def calculateLine(self):
        p1 = self.__object1.mapToGlobal(self.__object1.relation.geometry().center())
        p2 = self.__object2.mapToGlobal(self.__object2.relation.geometry().center())
        self.line.setPoints(p1, p2)

# Класс реализующий точку для создания связей
# При нажатии эмититься сигнал startPaintRelation, который перехватывает RelationOverlay для визуализации
# проведения линии между объектами
#
# При получении mouseReleaseEvent - проверяет, довел ли пользователь курсор до Object-a
# если да, то создает связь между родителем (который желательно тоже Object) и объектом под курсором
# после чего эмитит сигнал endPaintRelation созданным объектом Relation
class RelationPoint(QtWidgets.QFrame):
    startPaintRelation = pyqtSignal()
    endPaintRelation = pyqtSignal(Relation)

    def __init__(self, parent):
        super(RelationPoint, self).__init__(parent=parent)
        self.setGeometry((parent.width() / 2) - (RP_SIZE / 2), (parent.height() / 2), RP_SIZE, RP_SIZE)
        self.setStyleSheet("background-color: rgba(255,255,255,180); border-radius: "+str(RP_SIZE/2)+"px;")
        self.isPaintRelation = False
        self.relatedTo = []

    def find_obj(self, pos):
        obj = None

        widgets = []
        widget_at = QtWidgets.QApplication.instance().widgetAt(pos)
        while widget_at:
            if isinstance(widget_at, type(self.parent())):
                obj = widget_at
                break

            widget_at.setAttribute(Qt.WA_TransparentForMouseEvents)
            widgets.append(widget_at)
            widget_at = QtWidgets.QApplication.instance().widgetAt(pos)

        for widget in widgets:
            widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        return obj

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            self.isPaintRelation = True
            self.startPaintRelation.emit()

        QtWidgets.QFrame.mousePressEvent(self, e)


    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            self.isPaintRelation = False
            relation = None
            obj = self.find_obj(e.globalPos())

            if obj is not None and obj is not self.parent():
                for releatedRect in obj.relation.relatedTo:
                    if releatedRect is self.parent():
                        break
                else:
                    relation = Relation(obj, self.parent())

        self.endPaintRelation.emit(relation)
        QtWidgets.QFrame.mouseReleaseEvent(self, e)

# Класс реализующий графическое представление связей между объектами
class RelationsOverlay(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(RelationsOverlay, self).__init__(parent=parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.__mousePos = None
        self.__isPaintRelation = False
        self.__relationStartPoint = QPoint()
        self.__relations = []

    @property
    def mousePos(self):
        return self.__mousePos

    @mousePos.setter
    def mousePos(self, pos: QPoint):
        self.__mousePos = pos

    @property
    def isPaintRelation(self):
        return self.__isPaintRelation

    @isPaintRelation.setter
    def isPaintRelation(self, flag: bool):
        self.__isPaintRelation = flag

    @property
    def relations(self):
        return self.__relations

    def deleteRelation(self, r: Relation):
        if r is not None:
            self.relations.remove(r)
            del r
            self.update()

    def slotStartPaintRelation(self):
        self.__isPaintRelation = True
        self.__relationStartPoint = self.mapFromGlobal(QtGui.QCursor.pos())

    def slotEndPaintRelation(self, newRelation):
        self.__isPaintRelation = False
        if newRelation is not None:
            self.__relations.append(newRelation)

        self.update()
        self.__relationStartPoint = QPoint()

    def relationInPos(self, pos: QPoint):
        for relation in self.relations:
            # честно позаимствованный кусок со stackoverflow
            line = QLine(self.mapFromGlobal(relation.line.p1()), self.mapFromGlobal(relation.line.p2()))
            dx = pos.x() - line.x1();
            dy = pos.y() - line.y1();
            S = line.dx() * dy - dx * line.dy();
            ab = sqrt(line.dx() * line.dx() + line.dy() * line.dy());
            h = S / ab;
            if abs(h) < (L_SIZE / 2):
                return relation

        return None

    def paintEvent(self, event):
        q = QtGui.QPainter()
        q.begin(self)
        pen = QPen(Qt.black, L_SIZE, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin);
        q.setPen(pen)

        for relation in self.__relations:
            line = QLine(self.mapFromGlobal(relation.line.p1()), self.mapFromGlobal(relation.line.p2()))
            q.drawLine(line)

        if self.__mousePos and self.__isPaintRelation:
            q.drawLine(self.__mousePos.x(), self.__mousePos.y(), self.__relationStartPoint.x(), self.__relationStartPoint.y())
        q.end()