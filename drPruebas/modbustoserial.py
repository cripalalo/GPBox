#!/usr/bin/env python

import configSerie
import struct
import json
import time

class definiciones:
	FESTIVO1 = "01/01"
	FESTIVO2 = "06/01"
	FESTIVO3 = "29/02"
	FESTIVO4 = "24/03"
	FESTIVO5 = "25/03"
	FESTIVO6 = "13/04"
	FESTIVO7 = "02/05"
	FESTIVO8 = "26/05"
	FESTIVO9 = "15/08"
	FESTIVO10 = "12/10"
	FESTIVO11 = "01/11"
	FESTIVO12 = "06/12"
	FESTIVO13 = "08/12"
	FESTIVO14 = "26/12"
	
	flagD = 0
	flagM = 0

class PDU(object):

        """
        Convierte a hexadecimal a decimal los datos obtenidos por el puerto puerto serie
        """

        def dataCharge(self,datos):
                resultado = []
                for i in range(0,len(datos),2):
                        resultado.append(datos[i]*256+datos[i+1])

                return resultado

        def save(self,datos):
                resultado = []
                aux = 0
                aux1 = []
                f = open("/home/pi/Desktop/opalPruebas/resultados.txt","a")

                if len(datos) >0:
                        for i in range(0,len(datos),2):
                                resultado.append(float(datos[i])+float(datos[i+1])/10000)

                        json.dump(resultado,f)
                        f.write('\n')
                f.close()
		
		if len(datos) > 0:
			f = open("/usr/files/eBroker/calculos.txt","w")
			json.dump(resultado,f)
		f.close()


	def getTime(self):
		pt = [3,3,3,3,3,3,3,3,2,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2]

		hora = int(time.strftime("%H"))

		i = pt[hora]

		return i
	def getTypeDay(self):
		weekDay = time.strftime("%a")
		date = time.strftime("%d/%m")
	
		if (weekDay == "Sun") or (date == definiciones.FESTIVO1) or (date == definiciones.FESTIVO2) or (date == definiciones.FESTIVO3) or (date == definiciones.FESTIVO4) or (date == definiciones.FESTIVO5) or (date == definiciones.FESTIVO6) or (date == definiciones.FESTIVO7) or (date == definiciones.FESTIVO8) or (date == definiciones.FESTIVO9) or (date == definiciones.FESTIVO10) or (date == definiciones.FESTIVO11) or (date == definiciones.FESTIVO12) or (date == definiciones.FESTIVO13) or (date == definiciones.FESTIVO14):
			i = 3
		elif weekDay == "Sat":
			i = 2
		else:
			i = 1

		print weekDay,date

		return i

	def flags(self):
		hora = time.strftime("%H")
		minuto = time.strftime("%M")
		dia = int(time.strftime("%d"))

		if (dia == 1) and (hora == "00") and (minuto == "00") and (definiciones.hechoM == 0):
			definiciones.flagM = 1
			definiciones.hechoM = 1
		else:
			definciones.flagM = 0

		if (hora == "00") and (minuto == "00") and (definiciones.hechoD == 0):
			definiciones.flagD = 1
			definiciones.hechoD = 1
		else:
			definiciones.flagD = 0

		if (dia == 1) and (hora == "00") and (minuto == "01"):
			definiciones.hechoM = 0
		
		if (hora == "00") and (minuto == "01"):
			definiciones.hechoD = 0

class SCI(PDU):

        def send(self,trama):
		print len(trama)
                for i in range(0,len(trama)):
			if (i == 249) or (i == 250) or (i == 251) or (i == 252):
				configSerie.ser.write(struct.pack('B',trama[i]))
                       	elif i%3 == 0:
                                configSerie.ser.write(struct.pack('B',trama[i]))
                        else:
                                configSerie.ser.write(struct.pack('>H',trama[i]))

        def receive(self):

                datos = []

                for i in range(0,24):
                        dataLength = configSerie.ser.inWaiting()

                        if dataLength>0:
                                datos.append(configSerie.ser.read(1))

                                datos[i] = ord(datos[i])

                resultado = PDU.dataCharge(self,datos)
                print len(resultado)

                PDU.save(self,resultado)
		print "DATOS RECIBIDOS"
                print resultado
                return resultado


        def execute(self):
                        configSerie.ser.write(struct.pack('B',0))
                        print "Ejecucion eBroker"


class ModbusSerial(SCI):

        def __init__(self):
                self.trama = []

        def guardaDatos(self,datos):
                j = 0
                k = 0

                for i in range(0,3*len(datos)):
                        if i == 0:
                                self.trama.append(i)
                        #elif (i%2 == 0) and (j < 23):
                        #       self.trama.append(j)
                        #       j += 1
                        #elif (i%2 == 0) and(j >= 23):
                        #       self.trama.append(k)
                        #       k += 1
				entero = int(datos[0]*0.5)
				decimal = (float(datos[0])*0.5-entero)*10000
                        	self.trama.append(entero)
				self.trama.append(int(round(decimal)))

  

        #resultado.append(str.join("",("%04X" % entero)))
        #resultado.append(str.join("",("%04X" % int(round(decimal)))))


			elif i == 1:
				self.trama.append(i)
				entero = int(datos[0]*0.1)
				decimal = (float(datos[0])*0.1-entero)*10000
                        	self.trama.append(entero)
				self.trama.append(int(round(decimal)))

			elif i == 2:
				self.trama.append(i)
				entero = int(datos[0]*0.4)
				decimal = (float(datos[0])*0.4-entero)*10000
                        	self.trama.append(entero)
				self.trama.append(int(round(decimal)))

                """

                for i in range(0,len(trama)):
                        if i%3 == 0:
                                configSerie.ser.write(struct.pack('B',trama[i]))
                        else:
                                configSerie.ser.write(struct.pack('>H',trama[i]))
                """

                #SCI.execute(self)

        def readFile(self):
                j = 0
                k = 0
                l = 0
                m = 0
                n = 0

		
                #Se lee el fichero con las x y el fichero con los precios
                #with open("/usr/files/eBroker/x.txt","rb") as f:
                with open("/home/pi/Desktop/drPruebas/x.txt","rb") as f:
		        x = json.loads(f.read())


                for i in range(0,len(x),1):
                        if i%2 == 0:
                                self.trama.append(j)
                                j += 1
                        self.trama.append(int(str(x[i]),16))

                f.close()
		
                f = open("/home/pi/Desktop/opalPruebas/precio.txt","r")
                x = json.loads(f.read())


                for i in range(0,len(x),1):
                        if i%2 == 0:
                                self.trama.append(k)
                                k += 1
                        self.trama.append(int(str(x[i]),16))

                f.close()
		
		"""
                f = open("/home/pi/Desktop/opalPruebas/frecuencia.txt","r")
                x = json.loads(f.read())


                for i in range(0,len(x),1):
                        if i%2 == 0:
                                self.trama.append(l)
                                l += 1
                        self.trama.append(int(str(x[i]),16))

                f.close()



                f = open("/home/pi/Desktop/opalPruebas/potenciaSolar.txt","r")
                x = json.loads(f.read())


                for i in range(0,len(x),1):
                        if i%2 == 0:
                                self.trama.append(m)
                                m += 1
                        self.trama.append(int(str(x[i]),16))

                f.close()

                f = open("/home/pi/Desktop/opalPruebas/optimizacion.txt","r")
                x = json.loads(f.read())

                for i in range(0,len(x),1):
                        if i%2 == 0:
                                self.trama.append(n)
                                n += 1
                        self.trama.append(int(str(x[i]),16))
		


                f.close()

		tramo = PDU.getTime(self)
		tipo = PDU.getTypeDay(self)
	
		self.trama.append(tramo)	
		self.trama.append(tipo)
		self.trama.append(definiciones.flagD)
		self.trama.append(definiciones.flagM)
		"""
                SCI.send(self,self.trama)
                print "ESTA ES LA TRAMA: "
		print len(self.trama)
                print self.trama
                del self.trama[:]

