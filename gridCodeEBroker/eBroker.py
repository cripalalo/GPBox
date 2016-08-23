#!/usr/bin/env python

import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
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
		#--- Politica de reserva de la bateria ---#
		eresCoefT = np.array([0,6,12.18.24])
		eresCoefA = np.array([dato.x[0],dato.x[1],dato.x[2],dato.x[3],dato.x[0]])*definiciones.eMax*(definiciones.invPotNom**2)
		eresCoefB = np.array([dato.x[4]],dato.x[5],dato.x[6],dato.x[7],dato.x[4])*deficiones.eMax*definiciones.invPotNom
		eresCoefC = np.array([dato.x[8],dato.x[9],dato.x[10],dato.x[11],dato.x[8]])*deficiones.eMax
		eresCoefPPa = interpolate.interp1d(eresCoefT,eresCoefA,kind='cubic')
		eresCoefPPb = interpolate.interp1d(eresCoefT,eresCoefB,kind='cubic')
		eresCoefPPc = interpolate.interp1d(eresCoefT,eresCoefC,kind='cubic')
		potDRec = 1600		# Potencia recomendada de descarga
		potCRec = 900 		# Potencia recomendada de carga

		#--- Precios/Prioridades de los que intervienen ---#

		#--- Red 1: Red que recibe lo minimo para cumplir la normativa ---#
		preRed1D = 100 		# Precio de la red de normativa

		#--- Red 2: Red que recibe el resto ---#
		preRed2D = 60 		# Precio de la red del resto

		#--- Bateria 3: Reserva en bateria ---#
		preBat3O = 80		# Precio de oferta de la reserva de la bateria
		preBat3D = 70		# Precio de demanda de la reserva de la bateria

		#--- Bateria 4: Bateria que mueve el resto ---#
		preBat4O = 50 		# Precio de oferta del resto de la bateria
		preBat4D = 40 		# Precio de demanda del resto de la bateria

		#--- Panel 5: Panel fotovoltaico ---#
		prePan5O = 20 		# Precio de la oferta del panel

		#--- Aux 6: Reservatorio ficticio de energia usado para medir la cantidad de potencia por la que no se cumple la normativa y la que se deja de recibir del panel fotovoltaico por falta de uso
		preAux6O = 90 		# La venta de 6 se penaliza fuertemente porque no se cumple el grid code
		preAux6D = 30

		#--- FUNCION OBJETIVO ---#
		penalizacionInclumplimiento = 1000 		# Penalizacion por incumplimiento
		penalizacionVariacionSOC = 1000 		# Penalizacion por variar demasiado el SOC

		SOCdeseado = 70 	# SOC deseado
		SOClim1 = 80 		# Limites de las distintas zonas de penalizacion (10%-30%-50%-80%-90%)	
		SOClim2 = 50
		SOClim3 = 30

		penalizacionSOC1 = 0.3 		# Coeficiente de penalizacion en la zona cercana al SOC deseado (50% - 80%)
		penalizacionSOC2 = 0.9 		# Coeficiente de penalizacion en las zonas medias (30% - 50%) y (80% - 90%)
		penalizacionSOC3 = 3.0 		# Coeficiente de penalizacion en la zona mas alejada del SOC deseado (10% - 30%)

		SOCd1 = -(penalizacionSOC1/penalizacionSOC2)*(SOClim1-SOCdeseado)+SOClim1
		pSOC1 = (penalizacionSOC1*(SOClim1-SOCdeseado)**2)-(penalizacionSOC2*(SOClim1-SOCd1)**2)
		SOCd2 = -(penalizacionSOC1/penalizacionSOC2)*(SOClim2-SOCdeseado)+SOClim2
		pSOC2 = (penalizacionSOC1*(SOClim2-SOCdeseado)**2)-(penalizacionSOC2*(SOClim2-SOCd2)**2)
		SOCd3 = -(penalizacionSOC2/penalizacionSOC3)*(SOClim3-SOCd2)+SOClim3
		pSOC3 = (penalizacionSOC2*(SOClim3-SOCd2)**2)-(penalizacionSOC3*(SOClim3-SOCd3)**2)+pSOC2

		#--- Valores iniciales ---#
		respFrec = 0 		# Respuesta a frecuencia
		potRef = 0 			# Potencia dada como referencia (antes de incluir la respuesta en frecuencia)

		#--- Integrales ---#
		integralPotenciaNetaRed = 0
		integralPotenciaQueFalta = 0
		integralSaltosSOC = 0
		integralSaltosSOC = 0
		integralTiempo = 0
		botesSOC = 0
		integralSOC = 0


		#--- PROCESO ---#

		potRedNeta = 0
		potPanelNeta = 0
		potPanelBruta = 0
		SOC = 0

		""" Obtener la hora"""
		#--- Obtener periodo tarifario, fecha y tipo de dia ---#
		i = self.periodoTarifario()
		self.obtieneFecha()
		diaT = self.tipoDia()



		durInt = 24/float(definiciones.totalIntervalos)	# Ahora se ha puesto fijo
														# pero puede ser variable si se toma de un fichero,...

		frecInt = 1/durInt

		maxPotRefInc = rampMax*durInt

		# Potencia que se obtiene del panel. Se obtiene a partir de un fichero o similar

		potPan5O = np.amax(np.maximum(np.amin(np.minimum(a*r[0]+b^r[1]+c*r[3],definiciones.potNom)),0))

		potPanelBruta = potPan5O

		#--- Frecuencia de la red ---#
		frec = 0.0001*r[6]		# r se obtiene de un fichero o similar (es un dato que varia cada vez que se ejecuta el algoritmo)


		#--- Calculo de respuesta en frecuencia ---#
		if frec > frecRef:
			if frec >= frecSMax:
				respFrec = respMin
			else:
				respFMax = (frec-frecRMax)*kpos
				respFMin = (frec-frecRef)*kpos

				if respFrec > respFMax:
					respFrec = respFMax
				elif respFrec < respFMin:
					respFrec = respFMin
				elif respFrec >= 0:
					respFrec = 0
		else:
			if frec <= frecSMin:
				respFrec = respMax
			else:
				respFMax = (frec-frecRef)*kneg
				respFMin = (frec-frecRMin)*kneg
				if respFrec > respFMax:
					respFrec = respFMax
				elif respFrec < respMin:
					respFrec = respFMin
				elif respFrec <= 0:
					respFrec = 0


		if potRef < 0.1*potNom:
			respFrec = respFrec*10*potRef/float(potNom)

		potMinGridCode = respFrec + potRef - maxPotRefInc 		# Potencia minima que debe ir a la red

		if potMinGridCode > coefSobrecarga*potNom:
			potRed1D = coefSobrecarga*potNom
		elif potMinGridCode < 0:
			potRed1D = 0
			potMinGridCode = 0
		else:
			potRed1D = potMinGridCode

		potRed2D = respFrec + potRef + maxPotRefInc - potRed1D		# Margen entre potencia maxima y minima para la red
		potDisponible = potPan5O + potD

		if (respMax + potRef) > potDisponible:
			potRed2D = respFrec + potDisponible - respMax - potRed1D

		if (potRed2D + potRed1D) > coefSobrecarga*potNom:
			potRed2D = coefSobrecarga*potNom-potRed1D

		if potRed2D < 0:
			potRed2D = 0


		#--- Potencia que las baterias pueden dar/recibir para este intervalo ---#
		eresCoefa = eresCoefA(hora)
		eresCoefb = eresCoefB(hora)
		eresCoefc = eresCoefC(hora)

		eres = eresCoefa*(potRef**2) + eresCoefb*potRef + eresCoefc

		if eres >eMax:
			eres = eMax
		elif eres < 0:
			eres = 0

		if cargaBat > eres:
			potBat4O = np.amax(np.maximum(np.amin(np.minimum((cargaBateria-eres)*semiRedBat*frecInt,potDRec)),0)) 
			potBat3O = np.amax(np.maximum(np.amin(np.minimum(cargaBateria*semiRedBat*frecInt-potBat4O,potD-potBat4O)),0))
			potBat4D = np.amax(np.maximum(np.amin(np.minimum((eMax-cargaBateria)*invSemiRedBat*frecInt,potCRec)),0))
			potBar3D = 0
		else:
			potBat3O = np.amax(np.maximum(np.amin(np.minimum(cargaBateria*semiRedBat*frecInt,potD)),0))
			potBat4O = 0
			potBat3D = np.amax(np.maximum(np.amin(np.minimum((eres-cargaBateria)*invSemiRedBat*frecInt,potCRec)),0))
			potBat4D = np.amax(np.maximum(np.amin(np.minimum((eMax-cargaBateria)*invSemiRedBat*frecInt-potBat3D,potC-potBat3D)),0))

		#--- Montaje de las matrices de oferta y de demanda ---#
		dato.MO = np.zeros((definiciones.nDisp,5))
		dato.MO[:,0] = range(1,definiciones.nDisp+1)
		dato.MO[:,3] = 5
		dato.MD = dato.MO

		dato.MO[2,1] = potBat3O
		dato.MO[2,2] = preBat3O
		dato.MO[3,1] = potBat4O
		dato.MO[3,2] = preBat4D
		dato.MO[4,1] = potPan5O
		dato.MO[4,2] = prePan5O
		dato.MO[5,1] = potRed1D
		dato.MO[5,2] = preAux6O

		dato.MD[0,1] = potRed1D
		dato.MD[0,2] = preRed1D
		dato.MD[1,1] = potRed2D
		dato.MD[1,2] = preRed2D
		dato.MD[2,1] = potBat3D
		dato.MD[2,2] = preBat3D
		dato.MD[3,1] = potBat4D
		dato.MD[3,2] = preBat4D
		dato.MD[5,1] = potPan5O
		dato.MD[5,2] = preAux6D

		#--- LLAMADA AL EBROKER ---#
		(dato.MC,dato.MV) = self.eBroker()

		#--- Potencia bruta obtenida del panel fotovoltaico ---#
		potPanel = MV[np.nonzero(MV[:,0]==5)[0][:1],5]

		#--- Potencia neta obtenida del panel fotovoltaico ---#
		potPanelNeta = potPanel - MC[np.nonzero(MC[:,1]==6)[0][:,1],5]

		#--- Actualizando la carga de las baterias ---#
		potBatNeta = (MC[np.nonzero(MC[:,0]==3)[0][:1],5]) + MC[np.nonzero(MC[:,0]==4)[0][:1],5])*semiRedBat - (MV[np.nonzero(MV[:,0]==3)[0][:1],5] + MV[np.nonzero(MV[:,0]==4)[0][:1],5])*invSemiRedBat
		cargaBateria = cargaBateria + potBatNeta*durInt

		SOC = 80*cargaBateria/float(eMax) + 10

		#--- Actualizacion de la potencia que va a la red y componentes ---#

		potRed  = MC[np.nonzero(MC[:,0]==1)[0][:1],5]) + MC[np.nonzero(MC[:,0]==2)[0][:1],5]) - MV[np.nonzero(MV[:,0]==1)[0][:1],5]) - MC[np.nonzero(MC[:,0]==2)[0][:1],5])

		if potRed == 0:
			potRef = 0
			respFrec = 0
		else:
			potRef = potRed - respFrec

			if potRef < 0:
				potRef = 0
			elif potRef > coefSinSobrecarga*potNom:
				potRef = coefSinSobrecarga*potNom

		#--- Potencia que faltaba para cumplir el codigo de red ---#
		potDefecto = rendTransformador*potRed - potDefecto

		potRedNeta = rendTransformador*potRed - potDefecto

		#--- Integrales ---#
		integralPotenciaTeoricaPanel = integralPotenciaTeoricaPanel + (rendTransformador*potPan5O*durInt)
		integralPotenciaNetaRed = integralPotenciaNetaRed + (potRedNeta*durInt)
		integralPotenciaQueFalta = integralPotenciaQueFalta + (potDefecto*durInt)

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
