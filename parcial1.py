import numpy as np
from pyquaternion import Quaternion


class Herramientas:
    @staticmethod
    def rotar(self):
        return 0


class SubEspacio():
    """
    x, y, z - posicion de origen en parent
    parent - subespacio en el que estamos,
            si null, es un subespacio dentro del espacio base
    a, b, c - angulos de rotacion de
    """
    def __init__(self, x, y, z, a, b, c, parent: 'SubEspacio'):
        self.parent = parent
        self.x
        self.y
        self.z
        self.ax
        self.ay
        self.az

    def xAbs(self):
        return (self.parent.xAbs() if self.parent else 0) + self.x

    def yAbs(self):
        return (self.parent.yAbs() if self.parent else 0) + self.y

    def zAbs(self):
        return (self.parent.zAbs() if self.parent else 0) + self.z

    def xRel(self):
        return self.x

    def yRel(self):
        return self.y

    def zRel(self):
        return self.z


class Vec:
    def __init__(self, x, y, z, subespacio: SubEspacio):
        self.x = x
        self.y = y
        self.z = z
        self.subespacio = subespacio

    """
    returns absolute vector start point and absolute
            vector, point in sub-space would be start + vec
    """
    def vecAbs(self):
        start = [0,0,0]
        vec = [self.x, self.y, self.z]
        sub = self.subespacio
        while sub != None:
            xQuat = Quaternion(axis=[1,0,0], angle=-sub.a)
            yQuat = Quaternion(axis=[0,1,0], angle=-sub.b)
            zQuat = Quaternion(axis=[0,0,1], angle=-sub.c)

        return 0;

    def vecRel(self):
        return self
