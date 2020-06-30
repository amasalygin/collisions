from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRect, QPoint, QLine
from PyQt5.QtCore import pyqtSignal
import config
import random

from map import map
from relations import RelationPoint

random.seed()

# Родительский класс объектов на карте
class Object(QtWidgets.QFrame):
    objectMoved = pyqtSignal()
    def __init__(self, parent):
        super(Object, self).__init__(parent=parent)
        self.__oldPos = QPoint()          # предыдущая позиция курсора при перемещении
        self.__pressedDelta = QPoint()    # разница между координатами leftX, topY прямоугольника и координатами курсора
        self.relation = RelationPoint(self)


    def checkCollision(self, left, right):
        # если нет пересечений сразу выходим
        if not map.pointReserved(left.p1()) and not map.pointReserved(left.p2()) \
                and not map.pointReserved(right.p1()) and not map.pointReserved(right.p2()):
            return left

        done = False
        while not done:
            # если какая-либо из границ выходит за карту
            if (left.x1() > map.width) or (right.x1() > map.width) \
                    or (left.x1() < 0) or (right.x1() < 0):
                left.setP1(QPoint(self.geometry().x(), self.geometry().y())) # возвращяем текущее положение
                break

            # сдвигаемся вправо и пытаемся скорректировать по левой границе
            left.translate(self.width(), 0)
            right.translate(self.width(), 0)
            cleft, cright = self.correctByLeft(left, right)

            # Если остались пересечения
            if map.pointReserved(cleft.p1()) or map.pointReserved(cleft.p2()) \
                    or map.pointReserved(cright.p1()) or map.pointReserved(cright.p2()):
                continue
            else:
                left = cleft
                done = True

        return left

    # корректировка сторон по левой границе
    # bound - ближайшая свободная координату X справа от текущей
    # delta - разница между текущей X и ближайшей свободной
    def correctByLeft(self, left, right):
        bound = map.rightSerach(left.p1(), left.p2())
        delta = bound - left.x1()
        left.translate(delta, 0)
        right.translate(delta, 0)

        return left, right

    # корректировка сторон по правой границе
    # bound - ближайшая свободная координату X слева от текущей
    # delta - разница между текущей X и ближайшей свободной
    def correctByRight(self, left, right):
        bound = map.leftSearch(right.p1(), right.p2())
        delta = right.x1() - bound
        left.translate(-delta, 0)
        right.translate(-delta, 0)

        return left, right

    # проверка на пересечения -> свободная позиция для смещения
    def correctNewPosition(self, left: QLine, right: QLine) -> QPoint:
        if not map.rectInsideMap(QRect(left.x1(), left.y1(), self.width(), self.height())):
            return QPoint(self.geometry().x(), self.geometry().y())

        # Если левая граница заходит на занятые координаты
        if map.pointReserved(left.p1()) or map.pointReserved(left.p2()):
            left, right = self.correctByLeft(left, right)
        # Если правая граница заходит на занятые координаты
        elif map.pointReserved(right.p1()) or map.pointReserved(right.p2()):
           left, right = self.correctByRight(left, right)

        out = self.checkCollision(left, right)
        return out.p1()

    def mouseMoveEvent(self, e):
        if not self.relation.isPaintRelation:
            localPos = self.parent().mapFromGlobal(e.globalPos())
            delta = QPoint(localPos - self.__oldPos)

            x1 = self.__oldPos.x() + delta.x() - self.__pressedDelta.x()
            y1 = self.__oldPos.y() + delta.y() - self.__pressedDelta.y()
            x2 = x1 + self.width()
            y2 = y1 + self.height()

            left = QLine(QPoint(x1,y1), QPoint(x1,y2))
            right = QLine(QPoint(x2,y1), QPoint(x2,y2))

            # корректировка новой позиции для исключения наскока на другие объекты
            newPos = self.correctNewPosition(left, right)
            self.move(newPos)
            self.objectMoved.emit()

            self.__oldPos = localPos

        QtWidgets.QFrame.mousePressEvent(self, e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            map.lockPoints(self.geometry())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            localMousePos = self.parent().mapFromGlobal(e.globalPos())
            self.__oldPos = localMousePos
            self.__pressedDelta = QPoint(localMousePos.x() - self.x(), localMousePos.y() - self.y())
            map.unlockPoints(self.geometry())
            return # Не посылаем ивент дальше
        else:
            QtWidgets.QFrame.mousePressEvent(self, e)




# Rectangle(QtWidgets.QFrame)
# Класс реализующий прямоугольник, создаваемый при двойном клике по главному окну
# Конструктор принимает координаты X,Y точки клика, которые становяться его центром
class Rectangle(Object):
    def __init__(self, x, y, parent):
        super(Rectangle, self).__init__(parent=parent)
        self.setGeometry(x - (config.R_WIDTH / 2), y - (config.R_HEIGHT / 2), config.R_WIDTH, config.R_HEIGHT)
        self.setStyleSheet("QFrame{background-color: " + config.COLORS.get(random.randint(0, 9)) + ";}")



