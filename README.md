# Parcial 1 Dinamica
El codigo desarollado esta dentro de la carpeta parcial1/

En la siguiente foto esta contenida la definicion de los cuerpos y marcos utilizados:
![definicion de cuerpos](parcial1/definicion%20de%20cuerpos.jpg)

Como se nota en la imagen, existen los siguientes marcos de referencia:
* base
* b (bicicleta)
* ab (angulo bicicleta)
* f (rueda frontera)
* af (angulo rueda frontera)

Cada uno con sus respectivos angulos para definir diferentes inclinaciones, como el roll de la bicicleta, el angulo del manuvrio para voltear, y el pitch de la bicicleta tambien, para asegurarse de que la rueda frontera de la bicicleta siempre este en contacto con el piso.

A partir de esto se define la ubicacion de cada componente de la bicicleta. Para lograr definir su velocidad, se toman 2 lineas, 1 en cada rueda paralela al piso, se proyectan al plano x-y base, y se encuentra el punto donde 2 lineas perpendiculares a estas hacen interseccion. De esta manera se encuentra el centro instantaneo de movimiento de la bicicleta. Esto es en el caso que el angulo en el manuvrio sea mayor a 0, es decir, la bicicleta esta volteando. Si la bicicleta no esta volteando y va completamente recta, se encuentra facilmente el vector de velocidad de la bicicleta. Si en cambio la bicicleta si esta volteando, luego de encontrar el centro instantaneo para un instante, se utiliza este para encontrar la velocidad instantanea de la bicicleta en un punto especifico, es decir el punto definido como el centro de la bicicleta. Finalmente esta velocidad, junto con algunos angulos que definen la posicion de la bicicleta y algunas de sus coordenadas a lo largo del tiempo, se grafican para lograr visualizar las transformaciones realizadas.