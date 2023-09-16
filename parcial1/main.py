import numpy as np

from parcial1.clases import Punto, Subspace

# parametros bici (longitud en metros, angulos en grados,
# tiempo en segundos, velocidad angular en rad/s)
l = 1  # longitud entre ruedas (+)              (constante)
r = 0.5  # radio ruedas (+)                     (constante)
beta = 10  # angulo de tenedor (+)              (constante)
rho = 0  # angulo de inclinacion / roll         (variable - seleccionar)
phi = 0  # angulo manuvrio                      (variable - seleccionar)
psi = 0  # angulo pitch                         (variable - calculado)
theta = 0  # angulo visto desde arriba          (variable - calculado)
omega = 10  # velocidad angular rueda trasera   (variable - seleccionar)

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


def calcularPosicion():
    """
    calcula posicion para que rueda delantera toque el piso
    """
    centro_rueda, _ = centro_af.puntoAbs()
