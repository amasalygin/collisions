from PyQt5.QtCore import QRect
from config import R_WIDTH, R_HEIGHT
from enum import Enum
from objects.rectangle import Object, Rectangle
from map import map


class Objects(Enum):
    Rect = 1


class ObjectsFabric(object):
    @staticmethod
    def getObject(obj: Objects, x: int, y: int, parent=None) -> Object:
        if obj == Objects.Rect:
            r = Rectangle(x, y, parent)
            return r

        return None