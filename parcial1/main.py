import numpy as np
import numpy.linalg as lin

from parcial1.clases import Punto, Subspace

# parametros bici (longitud en metros, angulos en grados,
# tiempo en segundos, velocidad angular en rad/s)
# (constante) longitud entre ruedas
l = 1  #
# (constante) radio ruedas
r = 0.5  # [0.25, 0.75]
# (constante) angulo de tenedor
beta = 10  # [0, 45]
# (variable - seleccionar) angulo de inclinacion / roll
rho = 0  # [-45, 45]
# (variable - seleccionar) angulo manuvrio
phi = 0  # [-40, 40]
# (variable - calculado) angulo pitch
psi = 0
# (variable - calculado) angulo visto desde arriba
theta = 0
# (variable - seleccionar) velocidad angular rueda trasera
omega = 10  # [0.1, 100]
# (constante) tolerancia para decidir si rueda esta tocando piso
tolerancia = 0.001  # 0.001 (1mm)


# posiciones iniciales de marco b (cambian en el tiempo)
b_x = 0
b_y = 0
b_z = 0
# posiciones y angulo en y depende de posicion de la bici
b = Subspace(b_x, b_y, b_z, 0, 0, theta, None)
# posiciones de marco ab no cambian
# angulo cambia dependiendo de angulo de manuvrio (rueda delantera debe tocar piso)
ab = Subspace(0, 0, 0, 0, -psi, 0, b)
# posiciones de marco f no cambian
# angulo decidido por beta (angulo tenedor)
f = Subspace(l, 0, r, 0, -beta, 0, ab)
# posiciones de marco af no cambian
# cambia dependiendo de rotacion manuvrio
af = Subspace(0, 0, 0, 0, 0, phi, f)

# punto en centro de af (centro de rueda delantera)
centro_af = Punto(0, 0, 0, af)


def ajustarPsi():
    """
    ajusta posicion para que rueda delantera toque el piso
    se corre cada vez que se modifica el manuvrio
    """
    Subspace.definirContexto(b)
    n = 0
    # correr maximo 10 veces
    while n < 10:
        # coordenadas centro de rueda
        centro_rueda, _ = centro_af.puntoAbs()
        # un vector unitario en cordenada z negativo (hacia abajo)
        z_dn = [0, 0, -1]
        # vectores para definir plano afx-afz en espacio base (v1 y v2)
        _, v1 = Punto(0, 0, 1, af).puntoAbs()
        _, v2 = Punto(1, 0, 0, af).puntoAbs()
        # proyectar z_dn a plano v1-v2. Esta proyeccion se utiliza para encontrar el
        # punto mas bajo de la rueda (donde tocaria el piso)
        proy = v1.p() * (np.dot(v1.p(), z_dn)) + v2.p() * (np.dot(v2.p(), z_dn))
        # normalizar
        proy = proy / lin.norm(proy)
        # la linea que toca el piso en la rueda (spoke en rueda de bici)
        v3 = proy * r
        # vector de origen a punto que deberia tocar piso (dentro de plano afx-afz)
        v4 = centro_rueda + v3
        # si rueda de bici esta dentro de rango, no hay
        # necesidad de rotar bici, terminar de ajustar
        if v4[2] <= tolerancia:
            break
        # interseccion entre planos abz-abx y el plano formado por by-v4
        # el eje y del plano ab es ortogonal a abz-abx
        ort1 = Punto(0, 1, 0, ab).puntoAbs()[1].p()
        b_y = Punto(0, 1, 0, b).puntoAbs()[1].p()
        ort2 = np.cross(b_y, v4)
        # v5 es interseccion de planos
        v5 = np.cross(ort1, ort2)
        v5 = v5 / lin.norm(v5)
        # v5 debe estar en direccion positiva respecto al eje x de b
        if v5[0] < 0:
            v5 = v5 * (-1)
        # v6 -> proyeccion de v4 en v5
        v6 = ((np.dot(v4, v5)) / lin.norm(v5) ** 2) * v5
        # encontrar angulo entre v6 y eje x de ab
        ab_x = Punto(1, 0, 0, ab).puntoAbs()[1].p()
        angulo_rotacion = np.arccos(
            np.dot(ab_x, v6) / (lin.norm(ab_x) * lin.norm(v6)),
        )
        # coordenada z de v4 determina si toca rotar hacia
        # arriba o hacia abajo
        diff = v4[2]
        # rotar ab por angulo
        if diff < 0:
            ab.ay += angulo_rotacion
        elif diff > 0:
            ab.ay -= angulo_rotacion
        n += 1


def mover(dx, dy, daz):
    """
    la bici se puede trasladar en el plano x-y
    y puede rotar en el eje z como eje
    """
    pass
