

import numpy as np
import json
from estructuras import baterias as bateria
from estructuras import datos as dato
from estructuras import resultados as resultado
from definiciones import definiciones as definiciones



"""
optbrokerITVLAPALMA_3REDES
"""

def init():
	try:
	    f = open("/home/pi/Desktop/eBroker/datos.txt", "r") # or "a+", whatever you need

	except IOError:
		prueba()

def prueba():
	"""
	INICIALIZACION DE LAS VARIABLES
	"""
	picoCarga = np.zeros(3)
	energiaConsumida = np.zeros(1)
	costePotencia = np.zeros(1)
	costeEnergia = np.zeros(1)
	precioObat = np.zeros(9)
	precioDbat = np.zeros(9)
	cargaBateria = np.zeros(1)
	estadoCarga = np.zeros(1)

	cargaBateria[0] = 20.0
	estadoCarga[0] = 20.0

	MO = np.zeros((definiciones.nDisp,5))
	MO[:,0] = range(1,definiciones.nDisp+1)
	MD = MO

	MC = np.zeros((definiciones.nDisp,7))
	MV = MC

	data = {"potenciaBateria": np.zeros((1,definiciones.nBat)).tolist(),"cargaBateria": cargaBateria.tolist(),"estadoCarga": estadoCarga.tolist(),"picoCarga": picoCarga.tolist(), "energiaConsumida": energiaConsumida.tolist(), "costePotencia": costePotencia.tolist(), "costeEnergia": costeEnergia.tolist(), "precioObat": precioObat.tolist(), "precioDbat": precioDbat.tolist(), "MO": MO.tolist(), "MD": MD.tolist(), "MC": MC.tolist(), "MV": MV.tolist()}

	with open("/home/pi/Desktop/eBroker/datos.txt","w") as f:
		json.dump(data,f)
		f.close()

	"""
	dato.MO = np.zeros((definiciones.nDisp,5))
	dato.MO[:,0] = range(1,definiciones.nDisp+1)

	dato.MV = np.zeros((definiciones.nDisp,7))

	dato.MD = dato.MO
	dato.MC = dato.MV

	print dato.MO

	r = {"MO": dato.MO.tolist(), "MD": dato.MD.tolist()}

	with open("/home/pi/Desktop/eBroker/datos.txt","w") as json_file:
		json.dump(r,json_file)
		json_file.close()
	"""
"""
f = open("/home/pi/Desktop/eBroker/datos.txt","r")
x=json.loads(f.read())
r = np.array(x["MO"])
s = np.array(x["MD"])
print r
print s
f.close()
f = open("/home/pi/Desktop/eBroker/Modbus/x.txt","r")
x=json.loads(f.read())

dato.x = x
print "Valor de la posicion 23: %0.4f" % dato.x[22]
f.close()
"""


prueba()
