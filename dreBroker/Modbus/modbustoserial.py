#!/usr/bin/env python

import configSerie
import struct
import json

class PDU(object):

	"""
	Convierte a hexadecimal a decimal los datos obtenidos por el puerto puerto serie
	"""

	def dataCharge(self,datos):
		resultado = []
		for i in range(0,len(datos),2):
			resultado.append(datos[i]*256+datos[i+1])

		return resultado

class SCI(PDU):

	def send(self,trama):
		for i in range(0,len(trama)):
 			if i%3 == 0:
				configSerie.ser.write(struct.pack('B',trama[i]))
			else:
				configSerie.ser.write(struct.pack('>H',trama[i]))
	
	def receive(self):

		datos = []

		for i in range(0,8):
			dataLength = configSerie.ser.inWaiting()
			
			if dataLength>0:
				datos.append(configSerie.ser.read(1))

				datos[i] = ord(datos[i])

		resultado = PDU.dataCharge(self,datos)

		return resultado

		
	def execute(self):
			configSerie.ser.write(struct.pack('B',0))

class ModbusSerial(SCI):
	
	def __init__(self):
		self.trama = []

	def guardaDatos(self,datos):
		j = 0
		k = 0

		for i in range(0,len(datos)):
			if i == 0:
				self.trama.append(i)
			elif (i%2 == 0) and (j < 23):
				self.trama.append(j)
				j += 1
			elif (i%2 == 0) and(j >= 23):
				self.trama.append(k)
				k += 1

			self.trama.append(datos[i])

		for i in range(0,len(trama)):
 			if i%3 == 0:
				configSerie.ser.write(struct.pack('B',trama[i]))
			else:
				configSerie.ser.write(struct.pack('>H',trama[i]))

		SCI.send(self,self.trama)
		#SCI.execute(self)
		del self.trama[:]

	def storeFile(self,datos,name):
		a = []
		fichero = datos#json.loads(json.dumps(datos))
		#print fichero
		for i in range(0,len(fichero),2):
			a.append(float(int(fichero[i])) + float(int(fichero[i+1]))/10000)

		with open(name,'w') as outfile:
			json.dump(a,outfile)
			outfile.close()

		del a[:]



		"""
		with open('data.txt') as json_file:
			json_data = json.load(json_file)
			print(json_data)
		"""

		"""
		f = open('prueba.txt','w')
		f.write(str(datos))
		f.close
		f = open('prueba.txt','r')
		x = f.read()
		print x[1]
		print x[10]
		suma = float(x[1])+float(x[10])
		print suma
		"""

	def storeFile2(self,datos,name):
		a = []
		fichero = json.loads(json.dumps(datos))

		for i in range(0,len(fichero),2):
			a.append((float(fichero[i]*256**2)+float(fichero[i+1]))/1000000)

		with open(name,'w') as outfile:
			json.dump(a,outfile)
			outfile.close()


		del a[:]

	def convert(self,fichero,name):
		
		a = []

		for i in range(0,len(fichero),2):
			a.append(float(int(fichero[i])) + float(int(fichero[i+1]))/10000)

		#for i in range(len(fichero)-6,len(fichero),2):
		#	a.append((float(fichero[i]*256**2)+float(fichero[i+1]))/1000000)

		with open(name,'w') as outfile:
			json.dump(a,outfile)
			outfile.close()

		del a[:]
		
