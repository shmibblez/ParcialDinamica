import numpy as np
from pyquaternion import Quaternion


class Subspace:
    __contexto__: "Subspace | None" = None

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        ax: float,
        ay: float,
        az: float,
        parentSpace: "Subspace|None",
    ):
        """
        x, y, z - posicion de origen en parent
        parent - subespacio en el que estamos,
                si null, es un subespacio dentro del espacio base
        ax, ay, az - angulos a los cuales cada eje esta rotado
                - ej: si el eje x esta apuntando hacia uno, y ax = 10,
                rotaria clockwise 10 grados
        """
        self.parent = parentSpace
        self.x = x
        self.y = y
        self.z = z
        self.ax = ax
        self.ay = ay
        self.az = az

    @staticmethod
    def definirContexto(contexto):
        """
        define subespacio base (afecta los resultados
        retornados para posiciones absolutas)
        """
        Subspace.__contexto__ = contexto

    def vecOrigen(self):
        return Subspace.__aplicar__(
            [self.x, self.y, self.z],
            Subspace.__contexto__,
        )

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

    @staticmethod
    def __aplicar__(punto, sub: "Subspace | None"):
        """
        recursivo para comenzar desde los espacios bases
        punto es lista
        """
        if sub == None:
            return punto
        aplicado = Subspace.__aplicar__(punto, sub.parent)
        # restar origen
        aplicado = np.subtract(aplicado, sub.vecOrigen())
        # luego rotar
        xQuat = Quaternion(axis=[1, 0, 0], angle=sub.ax)
        yQuat = Quaternion(axis=[0, 1, 0], angle=sub.ay)
        zQuat = Quaternion(axis=[0, 0, 1], angle=sub.az)
        aplicado = xQuat.rotate(aplicado)
        aplicado = yQuat.rotate(aplicado)
        aplicado = zQuat.rotate(aplicado)

        return np.array(aplicado)

    def aplicar(self, punto: list[float]):
        """
        lleva vector a este subespacio
        (aplica sistema de coordenadas)
        """
        p = Subspace.__aplicar__(punto, self.parent)
        return Punto(p[0], p[1], p[2], self)


class Punto:
    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        parentSpace: Subspace | None,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.parentSpace = parentSpace

    def puntoAbs(self):
        """
        returns (start point coordinates, vector in top-most space)
                vector in top-most space is the same as vector in subspace,
                just in top-most space (diff coordinate sistem)
        """
        start = [0, 0, 0]
        vec = [self.x, self.y, self.z]
        parentSpace: Subspace | None = self.parentSpace
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
            parentSpace = parentSpace.parent

        start = np.array(start)
        vec = np.array(vec)

        start = Subspace.__aplicar__(start, Subspace.__contexto__)
        vec = Subspace.__aplicar__(vec, Subspace.__contexto__)
        return (
            Punto(start[0], start[1], start[2], Subspace.__contexto__),
            Punto(vec[0], vec[1], vec[2], Subspace.__contexto__),
        )

    def p(self):
        """
        retorna componentes como lista sin modificar
        """
        return np.array([self.x, self.y, self.z])
