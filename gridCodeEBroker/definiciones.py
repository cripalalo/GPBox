#!/usr/bin/env python

class definiciones:

	totalIntervalos = 96#288000				# Number of intervals in a day

	#-- Datos comunes --#

	potNom = 10000			# Potencia nominal del equipo en kW
	invPotNom = 1/potNom

	#-- Datos de la red --#

	rampMax = potNom*6			# Maxima rampa de potencia
	coefRespMaxFrec = 0.1 		# Maxima proporcion de la respuesta en frecuencia cib respecto a la potencia nominal
	frecRef = 60				# Frecuencia de referencia
	frecRMax = 60.012			# Frecuencia maxima antes de dar una respuesta
	frecRMin = 59.988 			# Frecuencia minima antes de dar una respuesta
	frecSMax = 60.3 			# Frecuencia máxima antes de saturar
	frecSMin = 59.7 			# Frecuencia minima antes de saturar
	respMin  = (-1)*coefRespMaxFrec*potNom 		# Respuesta para la frecuencia máxima (respuesta minimima)
	respMax = coefRespMaxFrec*potNom 			# Respuesta para la frecuencia minima (respuesta maxima)
	coefSobrecarga = 1.0 		# Coeficiente de sobrecarga maxima admitido en tanto por uno
	coefSinSobrecarga = 1.0 	# Maximo coeficiente de carga permitda para poder dar la respuesta en frecuencia sin sobrepasar el coeficiente de sobrecarga
	kpos = respMin/(frecSMax-frecRMax)	# Pendiente de respuesta para la desviacion positiva de la frecuencia
	kneg = respMax/(frecSMin-frecRMin)	# Pendiente de respuesta para desviacion negativa de la frecuencia

	#-- Datos del panel fotovoltaico --#
	a = 3.2586
	b = 9.5366
	c = -6.0207

	#-- Datos de las baterias --#
	potD = 4800 		# Potencia maxima descarga de las baterias (kW)
	potC = 2700 		# Potencia maxima carga de las baterias (kW)
	eMax = 1008 		# Energia maxima de las baterias (kWh). Los minimos siempre son 0
	cargaBat = 378 		# Energia inicial de la bateria (kWh)
	rendBat = 0.92 		# Rendimiento de la bateria (kWh que salen / kWh que entran)
	semiRendBat = rendBat**0.5 				# Rendimiento de entrada o salida de la bateria
	invSemiRendBat = 1/float(semiRendBat)	# La inversa de ese valor

class fecha:
	hora = []
	minuto = []
	dia = []	
