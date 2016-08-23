#!/usr/bin/env python

import numpy as np
import json
import time
import Modbus
import simplejson
from estructuras import baterias as bateria
from estructuras import datos as dato
from estructuras import resultados as resultado
from definiciones import definiciones as definiciones
from definiciones import fecha as fecha
from definiciones import festivos as festivo


class setting(object):
	def inicia(self):

		"""
		Se almacenan los datos en las estructuras
		"""
		# X optimizadas
		f = open("/usr/files/eBroker/x.txt","r")
		x=json.loads(f.read())
		dato.x = np.zeros(len(x)/2)
		if len(x) == 1:
			dato.x =x[0]
		else:
			for i in range(0,12,2):
				dato.x[i/2] = float(int(x[i],16))+float(int(x[i+1],16))/10000
		f.close()

		# Carga
		f = open("/home/pi/Desktop/carga.txt","r")
		x=json.loads(f.read())
		if len(x) == 1:
			dato.carga = x[0]
		else:
			dato.carga = x
		f.close()

		# Precio de la red
		f = open("/home/pi/Desktop/precio.txt","r")
		x = json.loads(f.read())

		if len(x) == 1:
			dato.precio = x["precio"]
		else:
			dato.precio = x

		f.close()

		# Datos
		f  = open("/home/pi/Desktop/eBroker/datos.txt","r")
		x = json.loads(f.read())


		bateria.potenciaBateria = np.array(x["potenciaBateria"])

		if len(x["cargaBateria"]) == 1:
			bateria.cargaBateria = x["cargaBateria"][0]
		else:
			bateria.cargaBateria = x["cargaBateria"]

		if len(x["estadoCarga"]) == 1:
			bateria.estadoCarga = x["estadoCarga"][0]
		else:
			bateria.estadoCarga = x["estadoCarga"]

		if len(x["picoCarga"]) == 1:
			resultado.picoCarga = x["picoCarga"][0]
		else:
			resultado.picoCarga = np.array(x["picoCarga"])

		if len(x["energiaConsumida"]) == 1:
			resultado.energiaConsumida = x["energiaConsumida"][0]
		else:
			resultado.energiaConsumida = np.array(x["energiaConsumida"])
		"""
		if len(x["costePotencia"]) == 1:
			resultado.costePotencia = x["costePotencia"][0]
		else:
		"""
		resultado.costePotencia = np.array(x["costePotencia"])

		if len(x["costeEnergia"]) == 1:
			resultado.costeEnergia = x["costeEnergia"][0]
		else:
			resultado.costeEnergia = np.array(x["costeEnergia"])

		if len(x["precioObat"]) == 1:
			dato.precioObat = x["precioObat"][0]
		else:
			dato.precioObat = np.array(x["precioObat"])
			dato.precioObat[0:3] = [dato.x[2],dato.x[1],dato.x[0]]

		if len(x["precioDbat"]) == 1:
			dato.precioDbat = x["precioDbat"][0]
		else:
			dato.precioDbat = np.array(x["precioDbat"])
			dato.precioDbat[0:3] = [dato.x[5],dato.x[4],dato.x[3]]

		if len(x["MO"]) == 1:
			dato.MO = x["MO"][0]
		else:
			dato.MO = np.array(x["MO"])

		if len(x["MD"]) == 1:
			dato.MD = x["MD"][0]
		else:
			dato.MD = np.array(x["MD"])

		if len(x["MC"]) == 1:
			dato.MC = x["MC"][0]
		else:
			dato.MC = np.array(x["MC"])

		if len(x["MV"]) == 1:
			dato.MV = x["MV"][0]
		else:
			dato.MV = np.array(x["MV"])

	def save(self):
		data = {"potenciaBateria": bateria.potenciaBateria.tolist(),"cargaBateria": np.array(bateria.cargaBateria).tolist(),"estadoCarga": np.array(bateria.estadoCarga).tolist(),"picoCarga": resultado.picoCarga.tolist(), "energiaConsumida": np.array(resultado.energiaConsumida).tolist(), "costePotencia": resultado.costePotencia.tolist(), "costeEnergia": resultado.costeEnergia.tolist(), "precioObat": dato.precioObat.tolist(), "precioDbat": dato.precioDbat.tolist(), "MO": dato.MO.tolist(), "MD": dato.MD.tolist(), "MC": dato.MC.tolist(), "MV": dato.MV.tolist()}
	
		#print data
		
		with open("/home/pi/Desktop/eBroker/datos.txt","w") as f:
			json.dump(data,f)
			f.close()

class eBroker(object):
	def proceso(self):
		print dato.carga
		print bateria.estadoCarga
		nBat = definiciones.nBat
		nLoad = definiciones.nLoad
		durInt = 24/float(definiciones.totalIntervalos)
		#potC = dato.x[21]
		#potD = dato.x[20]
		#eMax = dato.x[22]
		#potCont = dato.x[19]
		potC = 14.57
		potD = 14.57
		eMax = 100
		potCont = 36
		potBatO = []
		potBatD = []


		#--- RED TRAMO 1 ---#
		#potR1 = dato.x[18]
		potR1 = 22.35
		preRed1D = 0
		prioRed1O = 5
		prioRed1D = 5

		#--- RED TRAMO 2 ---#
		potR2 = 37.8 - potR1 
		preRed2D = 0
		prioRed2O = 5
		prioRed2D = 5

		#--- RED TRAMO 3 ---#
		potR3 = 1000
		preRed3D = 0
		prioRed3O = 5
		prioRed3D = 5

		prioBatO = 5
		prioBatD = 5

		prioLoad = 5

		#--- Obtener periodo tarifario, fecha y tipo de dia ---#
		i = self.periodoTarifario()
		self.obtieneFecha()
		diaT = self.tipoDia()

		if nBat > 0:
			#if (fecha.hora == 0) and (fecha.minuto == 0) and (definiciones.flagDay == 0):
			if dato.k == 95:
				definiciones.flagDay = 1
				potBatO.append(np.amin(np.minimum(np.amax(np.maximum(0,bateria.cargaBateria))*(1/durInt),potC)))
				potBatD.append(np.amin(np.minimum(np.amax(np.maximum(0,-bateria.cargaBateria))*(1/durInt),potD)))

			else:
				potBatO.append(np.amin(np.minimum(bateria.cargaBateria*(1/durInt),potC)))
				potBatD.append(np.amin(np.minimum(np.subtract(eMax,bateria.cargaBateria)*(1/durInt),potD)))

		#-- Se rellenan las matrices de oferta y de demanda ---#
		#--- RED 1 ---#
		dato.MO[0][1] = potR1
		dato.MD[0][1] = 0

		dato.MO[0][2] = float(dato.precio[i-1])
		dato.MD[0][2] = preRed1D

		dato.MO[0][3] = prioRed1O
		dato.MD[0][3] = prioRed1D

		#--- RED 2 ---#
		dato.MO[1][1] = potR2
		dato.MD[1][1] = 0

		dato.MO[1][2] = float(dato.precio[i-1]) + 0.1
		dato.MD[1][2] = preRed2D

		dato.MO[1][3] = prioRed2O
		dato.MD[1][3] = prioRed2D

		#--- RED 3 ---#
		dato.MO[2][1] = potR3
		dato.MD[2][1] = 0

		dato.MO[2][2] = float(dato.precio[i-1]) + 0.4
		dato.MD[2][2] = preRed3D

		dato.MO[2][3] = prioRed3O
		dato.MD[2][3] = prioRed3D

		#if diaT == 1:			# Dias laborables
		if nBat > 0:
			dato.MO[3:nBat+3,1] = potBatO[:]
			dato.MD[3:nBat+3,1] = potBatD[:]

			if i == 1:
				dato.MO[3:nBat+3,2] = dato.precioObat[0]
				dato.MD[3:nBat+3,2] = dato.precioDbat[0]
			elif i == 2:
				dato.MO[3:nBat+3,2] = dato.precioObat[1]
				dato.MD[3:nBat+3,2] = dato.precioDbat[1]
			elif i == 3:
				dato.MO[3:nBat+3,2] = dato.precioObat[2]
				dato.MD[3:nBat+3,2] = dato.precioDbat[2]

			dato.MO[3:nBat+3,3] = prioBatO
			dato.MD[3:nBat+3,3] = prioBatD
		"""
		elif diaT == 2:			# Sabados
			if nBat > 0:
				dato.MO[3:nBat+3,1] = potBatO[:]
				dato.MD[3:nBat+3,1] = potBatD[:]

				if i == 1:
					dato.MO[3:nBat+3,2] = dato.precioObat[3]
					dato.MD[3:nBat+3,2] = dato.precioDbat[3]
				elif i == 2:
					dato.MO[3:nBat+3,2] = dato.precioObat[4]
					dato.MD[3:nBat+3,2] = dato.precioDbat[4]
				elif i == 3:
					dato.MO[3:nBat+3,2] = dato.precioObat[5]
					dato.MD[3:nBat+3,2] = dato.precioDbat[5]

				dato.MO[3:nBat+3,3] = prioBatO
				dato.MD[3:nBat+3,3] = prioBatD
		elif diaT == 3:			# Dias festivos
			if nBat > 0:
				dato.MO[3:nBat+3,1] = potBatO[:]
				dato.MD[3:nBat+3,1] = potBatD[:]

				if i == 1:
					dato.MO[3:nBat+3,2] = dato.precioObat[6]
					dato.MD[3:nBat+3,2] = dato.precioDbat[6]
				elif i == 2:
					dato.MO[3:nBat+3,2] = dato.precioObat[7]
					dato.MD[3:nBat+3,2] = dato.precioDbat[7]
				elif i == 3:
					dato.MO[3:nBat+3,2] = dato.precioObat[8]
					dato.MD[3:nBat+3,2] = dato.precioDbat[8]

				dato.MO[3:nBat+3,3] = prioBatO
				dato.MD[3:nBat+3,3] = prioBatD
		"""
		#-- CARGAS --#
		if nLoad > 0:
			dato.MD[(nBat+3):(nLoad+nBat+3),1] = dato.carga
			dato.MD[nBat+3:nLoad+nBat+3,2] = float(float(dato.precio[i-1])) + 0.4 + 0.1
			dato.MD[nBat+3:nLoad+nBat+3,3] = prioLoad

		#--- LLAMADA AL EBROKER ---#
		(dato.MC,dato.MV) = self.eBroker()

		#--- POTENCIA COMPRADA A LA RED ---#
		potComp1 = dato.MV[np.where(dato.MV[:,0]==1),5] - dato.MC[np.where(dato.MC[:,0]==1),5]
		potComp2 = dato.MV[np.where(dato.MV[:,0]==2),5] - dato.MC[np.where(dato.MC[:,0]==2),5]
		potComp3 = dato.MV[np.where(dato.MV[:,0]==3),5] - dato.MC[np.where(dato.MC[:,0]==3),5]

		print "Potencias compradas a la red 1, 2 y 3: ",potComp1,potComp2,potComp3

		for j in range(0,nBat,1):
			bateria.potenciaBateria[j] = dato.MC[np.where(dato.MC[:,0]==j+4),5] - dato.MV[np.where(dato.MV[:,0]==j+4),5]
			bateria.cargaBateria = bateria.cargaBateria + bateria.potenciaBateria[j]*durInt

		if nBat > 0:
			bateria.estadoCarga = bateria.cargaBateria

		resultado.energiaConsumida = resultado.energiaConsumida + (potComp1+potComp2+potComp3)*durInt
		resultado.costeEnergia = resultado.costeEnergia + float(dato.precio[i-1])*(potComp1+potComp2+potComp3)*durInt

		print "Coste de energia: ", resultado.costeEnergia
		print "Energia consumida: ", resultado.energiaConsumida

		data = {"Coste de energia": resultado.costeEnergia.tolist(), "Energia consumida": resultado.energiaConsumida.tolist()}

		with open("/home/pi/Desktop/eBroker/resultadoRT.txt","a+") as f:
			json.dump(data,f)
			f.write("\n")
			f.close()


		#--- PICO DE CARGA ---#

		pot = potComp1+potComp2+potComp3

		if pot > resultado.picoCarga[i-1]:
			resultado.picoCarga[i-1] = pot

		if (fecha.dia == 1) and (fecha.hora == 0) and (fecha.minuto == 0) and (definiciones.flagMonth == 0):
		#if dato.intervalo == 2976:
			resultado.costePotencia = 0;

			for j in range(0,3,1):
				if resultado.picoCarga[j] < 0.85*definiciones.potCont:
					resultado.costePotencia = resultado.costePotencia + definiciones.tp1[j]*0.85*definiciones.potCont
				elif resultado.picoCarga[j] > 1.05*definiciones.potCont:
					resultado.costePotencia = resultado.costePotencia+definiciones.tp1[j]*(resultado.picoCarga[j]+2*(resultado.picoCarga[j]-1.05*definiciones.potCont))
				else:	
					resultado.costePotencia = resultado.costePotencia+definiciones.tp1[j]*resultado.picoCarga[j]

			resultado.costePotencia = resultado.costePotencia/12

			f = resultado.costePotencia + resultado.costeEnergia
			print "La factura asciende a: %0.2f" % f
		
		"""
		dato.k += 1
		dato.intervalo += 1

		if dato.k == 96:
			dato.k = 0

		if dato.intervalo > 2976:
			dato.intervalo = 1
		"""

	def eBroker(self):
		valoriD = np.zeros((1,5))	# Valor de los precios de demanda
		valoriO = []	# Valor de los precios de oferta
		EAD = 0
		EAO = 0
		A = np.zeros((definiciones.nDisp,1))
		MD = np.append(dato.MD,A,axis=1)
		MO = np.append(dato.MO,A,axis=1)

		# Ordenacion de las demandas
		MD = np.array(sorted(MD,key=lambda l:(-l[3],-l[2],-l[1],l[0])))

		valoriD = MD[:,1].tolist()

		# Ordenacion de las ofertas
		MO = np.array(sorted(MO,key=lambda l:(-l[3],l[2],l[1],l[0])))

		valoriO = MO[:,1].tolist()

		# Equipos en oferta y en demanda
		ED = len(MD)
		EO = len(MO)

		while EAD < ED:
			EAO = 0

			"""
			Los equipos cuya demanda es cero no necesitan
			negociar, su estado se pone a existe y se pasa
			al siguiente
			"""

			if MD[EAD,1] == 0:
				MD[EAD,4] = 1
				EAD += 1
			else:
				while EAO < EO:
					if MO[EAO,1] == 0:
						MO[EAO,4] = 1
						EAO += 1
					else:
						# Si el precio de la demanda es mayor o igual
						# al de la oferta, se puede negociar
						if MD[EAD,2] >= MO[EAO,2]:
							# Si el valor de la oferta y la demanda son iguales,
							# se intercambian el valor completo
							if MD[EAD,1] == MO[EAO,1]:
								# Se almacena el precio de la casacion
								MD[EAD,5] = MD[EAD,5]+(MD[EAD,1]*MD[EAD,2]+MO[EAO,1]*MO[EAO,2])/2
								MO[EAO,5] = MO[EAO,5]+(MD[EAD,1]*MD[EAD,2]+MO[EAO,1]*MO[EAO,2])/2
								MD[EAD,1] = 0
								MO[EAO,1] = 0
								MD[EAD,4] = 1
								MO[EAO,4] = 1

								EAO = EO + 1 	# Ya se ha cumplido esta demanda
							# La oferta puede completarse y aun restara algo de oferta
							elif MD[EAD,1] < MO[EAO,1]:
								# Se almacena el precio de la casacion
								MD[EAD,5] = MD[EAD,5]+(MD[EAD,1]*MD[EAD,2]+MD[EAD,1]*MO[EAO,2])/2
								MO[EAO,5] = MO[EAO,5]+(MD[EAD,1]*MD[EAD,2]+MD[EAD,1]*MO[EAO,2])/2
								MO[EAO,1] = MO[EAO,1]-MD[EAD,1]
								MD[EAD,1] = 0
								MD[EAD,4] = 1
								MO[EAO,4] = 1

								EAO = EO + 1
							# No se cubre totalmente la demanda
							else:
								# Se almacena el precio de la casacion
								MD[EAD,5] = MD[EAD,5]+(MO[EAO,1]*MO[EAO,2]+MO[EAO,1]*MD[EAD,2])/2
								MO[EAO,5] = MO[EAO,5]+(MO[EAO,1]*MO[EAO,2]+MO[EAO,1]*MD[EAD,2])/2
								MD[EAD,1] = MD[EAD,1]-MO[EAO,1]
								MO[EAO,1] = 0
								MD[EAD,4] = 1
								MO[EAO,4] = 1

								EAO += 1
						else:
							EAO += 1
				EAD += 1				
		

		MD[:,1] = valoriD-MD[:,1]
		MO[:,1] = valoriO-MO[:,1]

		# El valor final de lo que se intercambia sera lo que se pretendia intercambiar
		# menos lo que no se intercambio

		MD[np.nonzero(MD[:,1]),5] = MD[np.nonzero(MD[:,1]),5]/MD[np.nonzero(MD[:,1]),1]
		MO[np.nonzero(MO[:,1]),5] = MO[np.nonzero(MO[:,1]),5]/MO[np.nonzero(MO[:,1]),1]

		# Precio medio ponderando los precios por los valores aportados

		# Potencia consumida
		PC = sum(MD[:,1]*MD[:,4])

		# Potencia aportada
		PA =  sum(MO[:,1]*MO[:,4])

		# Precio Demanda (dinero generado en la demanda)
		PDT = sum(MD[:,1]*MD[:,5])

		# Precio oferta (dinero generado en la oferta)
		POT = sum(MO[:,1]*MO[:,5])

		NED = np.count_nonzero(MD[:,1])

		NEO = np.count_nonzero(MO[:,1])

		MD = MD[:,(0,1,2,3,4,1,5)]

		MO = MO[:,(0,1,2,3,4,1,5)]


		MD[:,1] = valoriD
		MO[:,1] = valoriO

		return MD,MO

	def periodoTarifario(self):
		#return definiciones.pt[int(dato.k/4)]
		return definiciones.pt[int(time.strftime("%H"))]

	def obtieneFecha(self):
		fecha.hora = int(time.strftime("%H"))
		fecha.minuto = int(time.strftime("%M"))
		fecha.dia  = int(time.strftime("%d"))

	def tipoDia(self):
		dia = time.strftime("%d/%m")
		diaSemana = time.strftime("%a")
		i = 0

		if (diaSemana == "Sun") or (dia == festivo.festivo1) or (dia == festivo.festivo2) or (dia == festivo.festivo3) or (dia == festivo.festivo4) or (dia == festivo.festivo5) or (dia == festivo.festivo6) or (dia == festivo.festivo7) or (dia == festivo.festivo8) or (dia == festivo.festivo9) or (dia == festivo.festivo10) or (dia == festivo.festivo11) or (dia == festivo.festivo12) or (dia == festivo.festivo13) or (dia == festivo.festivo14):
			i = 3  		# Dia festivo
		elif diaSemana == "Sat":
			i = 2 		# Sabado
		elif (diaSemana == "Mon") or (diaSemana == "Tue") or (diaSemana == "Wed") or (diaSemana == "Thu") or (diaSemana == "Fri"):
			i = 1 		# Dia laboral

		return i



























"""
INICIALIZACION DE VARIABLES
"""
"""
durInt = 24/float(definiciones.totalIntervalos)		# duracion del intervalo
potC = dato.x[21]									# Potencia maxima de las baterias
potD = dato.x[20]									# Potencia minima de las baterias
eMax = dato.x[22] 									# Energia maxima de las baterias
tp1 = [59.173468,36.490689,8.367731]
k = 288000

bateria.cargaBateria = 0

potCont = dato.x[19] 								# Potencia contratada

potR1 = dato.x[18]

potR2 = definiciones.potCont - dato.x[18]

potR3 = definiciones.maxPotencia

#print durInt
"""

"""
Inicializacion de algunas variables de las estructuras
"""
"""
if definiciones.nBat > 0:
	if k == definiciones.totalIntervalos:
		potBatO = np.amin(np.minimum(np.amax(np.maximum(0,bateria.cargaBateria))*(1/durInt),potC))
		potBatD = np.amin(np.minimum(np.amax(np.maximum(0,-bateria.cargaBateria))*(1/durInt),potD))

	else:
		potBatO = np.amin(np.minimum(bateria.cargaBateria*(1/durInt),potC))
		potBatD = np.amin(np.minimum(np.subtract(bateria.eMax,bateria.cargaBateria)*(1/durInt,potD)))


		#print potBatO

"""
