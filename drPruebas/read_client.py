#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lectura en el ESCLAVO

"""
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient as ModbusTcpClient
from modbustoserial import *

import time
import json

#-----------------------------------#
# Configuracion del log del MAESTRO #
#-----------------------------------#

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

#-----------------#
#    VARIABLES    #
#-----------------#

i=0
j=0
t0=time.time()
decoded = []
dato = []
modbus = ModbusSerial()
charge = 0

#--------------------------#
# Conexion MAESTRO-ESCLAVO #
#--------------------------#

#client = ModbusTcpClient('192.168.10.101','1502')
client = ModbusTcpClient('192.168.10.55')
client.connect()
print "CONNECT"
address = 0x00
#---------------#
#    PAYLOAD    #
#---------------#
def readPayload():
        global address          #Direccion del primer registros
        count = 2              #Numero de registros a leer
	
	global charge

        """
        Se lee cada uno de los registros y se añade a un array que posteriorme se enviara a traves del puerto serie al DSP
        """

	for i in range(0,count):
        	result = client.read_holding_registers(address+i,1,unit=0x01)
        	decoder = BinaryPayloadDecoder.fromRegisters(result.registers, endian = Endian.Big)
        	decoded.append(decoder.decode_16bit_uint())
		address += i
	address += 1

	if address == 192:
		address = 0x00
	charge += float(decoded[0])

	f = open("/usr/files/eBroker/charge.txt","w")
	json.dump(charge,f)
	f.close()


	f = open("/usr/files/eBroker/carga.txt","w")
	json.dump(decoded[0],f)
	f.close()

	modbus.guardaDatos(datos=decoded)
        modbus.readFile()
	del decoded[:]

        return modbus.receive()


def writePayload(dato):
        address = 0x64          #Dirección de memoria del primer registro de escritura
	#address = 0x36
        """
        Se escribiran tantos registros como bytes tenga la trama de datos recibida a traves del puerto serie
        """

        for i in range(0,2):
                builder = BinaryPayloadBuilder(endian=Endian.Big)

                builder.add_16bit_uint(dato[i])

                payload = builder.build()
                client.write_registers(address+i,payload,unit=0x02,skip_encode=True)

        del dato[:]

"""
builder = BinaryPayloadBuilder(endian=Endian.Big)

builder.add_16bit_uint(0)


payload = builder.build()
client.write_registers(0x66,payload,unit=0x02,skip_encode=True)



builder = BinaryPayloadBuilder(endian=Endian.Big)

builder.add_16bit_uint(1)


payload = builder.build()
client.write_registers(0x66,payload,unit=0x02,skip_encode=True)
"""
t0 = time.time()
time.sleep(0.5)
#for i in range(0,2976):
for i in range(0,97):
#while 1:
	t2 = time.time()
        
	dato = readPayload()
	
#	while len(dato) == 0:
#		time.sleep(1)
#		dato = readPayload()	
	"""
	if dato:
		writePayload(dato)
	"""
	t1 = time.time()
	print "Tardo en ejecutar:"
	print t1-t2
	while time.time()-t0 < 1:
	        pass
	t0=time.time()
#	del dato[:]
