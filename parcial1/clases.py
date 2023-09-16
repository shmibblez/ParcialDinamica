import numpy as np
from pyquaternion import Quaternion


class Subspace:
    """
    x, y, z - posicion de origen en parent
    parent - subespacio en el que estamos,
            si null, es un subespacio dentro del espacio base
    ax, ay, az - angulos a los cuales cada eje esta rotado
            - ej: si el eje x esta apuntando hacia uno, y ax = 10,
            rotaria clockwise 10 grados
    """

    def __init__(self, x, y, z, ax, ay, az, parentSpace: "Subspace|None"):
        self.parent = parentSpace
        self.x = x
        self.y = y
        self.z = z
        self.ax = ax
        self.ay = ay
        self.az = az

    def vecOrigen(self):
        return [self.x, self.y, self.z]

    # def xAbs(self):
    #     return (self.parent.xAbs() if self.parent else 0) + self.x

    # def yAbs(self):
    #     return (self.parent.yAbs() if self.parent else 0) + self.y

    # def zAbs(self):
    #     return (self.parent.zAbs() if self.parent else 0) + self.z

    # def xRel(self):
    #     return self.x

    # def yRel(self):
    #     return self.y

    # def zRel(self):
    #     return self.z


class Punto:
    def __init__(self, x, y, z, parentSpace: Subspace):
        self.x = x
        self.y = y
        self.z = z
        self.parentSpace = parentSpace

    """
    returns start point coordinates and vector in top-most space
    """

    def puntoAbs(self):
        start = [0, 0, 0]
        vec = [self.x, self.y, self.z]
        parentSpace = self.parentSpace
        while parentSpace != None:
            xQuat = Quaternion(axis=[1, 0, 0], angle=-parentSpace.ax)
            yQuat = Quaternion(axis=[0, 1, 0], angle=-parentSpace.ay)
            zQuat = Quaternion(axis=[0, 0, 1], angle=-parentSpace.az)
            start = xQuat.rotate(start)
            start = yQuat.rotate(start)
            start = zQuat.rotate(start)
            vec = xQuat.rotate(vec)
            vec = yQuat.rotate(vec)
            vec = zQuat.rotate(vec)
            start = np.add(start, parentSpace.vecOrigen())
            parentSpace = self.parentSpace.parent

        return (start, vec)
