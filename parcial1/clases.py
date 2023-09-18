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

    def vecOrigenRel(self):
        """
        retorna vector de coordenadas con respecto al
                marco dentro del cual esta
        """
        return Punto(self.x, self.y, self.z, self.parent)

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
            # print(">saliendo aplicar")
            return np.array(punto)
        subVec = Subspace.__aplicar__(punto, sub.parent)
        # restar origen
        # print("0antes aplicar: {}".format(aplicado))
        subVec = np.subtract(subVec, [sub.x, sub.y, sub.z])
        # luego rotar
        zQuat = Quaternion(axis=[0, 0, 1], degrees=-sub.az)
        yQuat = Quaternion(axis=[0, 1, 0], degrees=-sub.ay)
        xQuat = Quaternion(axis=[1, 0, 0], degrees=-sub.ax)
        # print("*antes aplicar: {}".format(aplicado))
        subVec = zQuat.rotate(subVec)
        subVec = yQuat.rotate(subVec)
        subVec = xQuat.rotate(subVec)
        # print("*luego aplicar: {}".format(aplicado))

        return np.array(subVec)

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
                just in top-most space (diff coordinate system)
        """
        start = [0, 0, 0]
        vec = [self.x, self.y, self.z]
        parentSpace: Subspace | None = self.parentSpace
        # print("parentSpace: " + str(parentSpace))
        while parentSpace != None:
            # print("parent space origen abs: {}".format(parentSpace.vecOrigen()))
            # print("parent space origen rel: {}".format(parentSpace.vecOrigenRel().p()))
            xQuat = Quaternion(axis=[1, 0, 0], degrees=-parentSpace.ax)
            yQuat = Quaternion(axis=[0, 1, 0], degrees=-parentSpace.ay)
            zQuat = Quaternion(axis=[0, 0, 1], degrees=-parentSpace.az)
            # add parent vec to start
            start = np.add(np.array(start), parentSpace.vecOrigen())
            # no toca rotar punto de referencia
            # start = xQuat.rotate(start)
            # start = yQuat.rotate(start)
            # start = zQuat.rotate(start)
            # rotate vector
            vec = xQuat.rotate(vec)
            vec = yQuat.rotate(vec)
            vec = zQuat.rotate(vec)
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
