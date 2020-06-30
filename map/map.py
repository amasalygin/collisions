from PyQt5.QtCore import QRect, QPoint,QObject, QSize
from PyQt5.QtWidgets import QWidget

# Обертка для работы с двумерным массивом координат
# каждая пустая координата = 0
# каждая занятая = 1

class CoordsMap(QObject):
    def __init__(self, width: int, height: int, parent=None):
        super(CoordsMap, self).__init__(parent=parent)

        self.__map = [[0] * height] * width
        self.__width = width
        self.__height = height
        self.__areaWidget = None

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def areaWidget(self):
        return self.__areaWidget

    @areaWidget.setter
    def areaWidget(self, area: QWidget):
        self.__areaWidget = area
        self.resizeMap(area.size())

    def resizeMap(self, size: QSize):
        if size.width() > self.__width:
            delta = size.width() - self.__width
            for i in range(delta):
                list = [0] * size.height()
                self.__map.append(list)
        elif size.width() < self.__width:
            delta = self.__width - size.width()
            for i in range(delta):
                self.__map.pop(-1)

        if size.height() > self.__height:
            for i in range(self.__height):
                delta = size.height() - len(self.map[i])
                for count in range(delta + 1):
                    self.__map[i].append(0)

        elif size.height() < self.__height:
            delta = self.__height - size.height()
            for i in range(size.width()):
                for count in range(delta + 1):
                    self.__map[i].pop(-1)

        self.__width = size.width()
        self.__height = size.height()

    # освобождение координат
    def unlockPoints(self, rect: QRect):
        if not self.rectInsideMap(rect):
            return

        for i in range(rect.x(), rect.x() + rect.width()):
            for j in range(rect.y(), rect.y() + rect.height()):
                self.__map[i][j] = 0

    # блокировка координат
    def lockPoints(self, rect: QRect):
        if not self.rectInsideMap(rect):
            return

        for i in range(rect.x(), rect.x() + rect.width()):
            for j in range(rect.y(), rect.y() + rect.height()):
                self.__map[i][j] = 1


    # Поиск координаты X при которой прямая [p1;p2] ни с кем не пересекатеся - в сторону возрастания X
    def rightSerach(self, p1: QPoint, p2: QPoint):
        bound = 0
        for i in range(p1.x(), self.__width):           # Проход по X : от p1.x() до конца карты
            for j in range(p1.y(), p2.y() + 1):         # Проход по Y : от p1.y() до p2.y()
                if self.pointReserved(QPoint(i, j)):    # Если точка на прямой [{i;y1}, {i;y2}] занята
                    break                               # переходим к следующей координате X
            else:
                bound = i                               # Если на прямой [{i;y1}, {i;y2}] нет занятых
                break                                   # Прекращяем поиск

        return bound

    # Поиск координаты X при которой прямая [p1;p2] ни с кем не пересекатеся - в сторону убывания X
    def leftSearch(self, p1: QPoint, p2: QPoint):
        bound = 0
        for i in range(p1.x(), 0, -1):
            for j in range(p1.y(), p2.y() + 1):
                if self.pointReserved(QPoint(i, j)):
                    break
            else:
                bound = i
                break

        return bound

    # проверка блокировки координаты
    def pointReserved(self, p: QPoint):
        if self.pointInsideMap(p):
            return self.__map[p.x()][p.y()] == 1

        return True

    # проверка на вхождение QPoint в область координат
    def pointInsideMap(self, p: QPoint):
        if (p.x() >= 0) and (p.x() < self.__width) and (p.y() >= 0) and (p.y() < self.__height):
            return True

        return False

    # проверка на вхождение QRect в область координат
    def rectInsideMap(self, rect: QRect) -> bool:
        topLeft = QPoint(rect.x(), rect.y())
        bottomRight = QPoint(rect.x() + rect.width(), rect.y() + rect.height())

        return self.pointInsideMap(topLeft) and self.pointInsideMap(bottomRight)


    # проверка на пересечение с входным QRect
    def rect_intersects(self, rect: QRect):
        if not self.rectInsideMap(rect):
            return True

        topLeft = QPoint(rect.x(), rect.y())
        topRight = QPoint(rect.x() + rect.width(), rect.y())
        bottomLeft =  QPoint(rect.x(), rect.y() + rect.height())
        bottomRight = QPoint(rect.x() + rect.width(), rect.y() + rect.height())

        if not self.pointReserved(topLeft) and not self.pointReserved(bottomRight)\
                and not self.pointReserved(topRight) and not self.pointReserved(bottomLeft):
            return False
        else:
            return True