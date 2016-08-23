#!/usr/bin/env python

import struct
import ficheros
import definiciones

# Definicion de varibles globales
aux = 0



def convierte(tipo,dato):
    entero = 0
    decimal = 0

    if  tipo == 1:
        entero = int(dato)
        decimal = float((dato - entero)*10000)

    elif tipo == 2:
        entero = int(dato)
        decimal = float((dato - entero)*1000000)

    return entero,int(float(str(decimal)))

def escribeUSB(tipo):
        global aux

        if tipo==0:
                definiciones.ser.write(struct.pack('B',0))
        elif tipo==1:
            for i in range(1):
                (entero,decimal)=convierte(1,ficheros.carga[i])
                definiciones.ser.write(struct.pack('B',2) + struct.pack('B',i) + struct.pack('>h', entero) + struct.pack('>h', decimal))
               # print "Carga enviada"
               # print entero
               # print decimal

                del ficheros.carga[:]
        elif tipo==2:
                print tipo
        elif tipo==3:
                for i in range(23):
                    (entero,decimal)=convierte(1,ficheros.resultado[i])
                    aux += 1
                    definiciones.ser.write(struct.pack('B',1) + struct.pack('B',i) + struct.pack('>h', entero) + struct.pack('>h',decimal))
                   # print "Lectura enviada"

                del ficheros.resultado[:]
        elif tipo==4:
                for i in range(3):
                    (entero,decimal)=convierte(2,ficheros.precio[i])
                    definiciones.ser.write(struct.pack('B',3) + struct.pack('B',i) + struct.pack('>h',entero) + struct.pack('>I',decimal))
                    #print "Precio enviado"
                del ficheros.precio[:]
	elif tipo==10:
                definiciones.ser.write(struct.pack('B',10))
        elif tipo==8:
                definiciones.ser.write(struct.pack('B',8))

