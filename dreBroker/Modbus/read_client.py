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
from .. import inicializacion
from ..eBroker import setting
from ..eBroker import eBroker

import time

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
address = 0x00
unidad = 0x01

#--------------------------#
# Conexion MAESTRO-ESCLAVO #
#--------------------------#

client = ModbusTcpClient('192.168.10.55')
client.connect()
print "CONNECT"

#---------------#
#    PAYLOAD    #
#---------------#
def readPayload():
        global address          #Direccion del primer registros
        global unidad
	count = 2              #Numero de registros a leer

        """
        Se lee cada uno de los registros y se añade a un array que posteriorme se enviara a traves del puerto serie al DSP
        """

	for i in range(0,2):
        	result = client.read_holding_registers(address+i,1,unit=unidad)
        	decoder = BinaryPayloadDecoder.fromRegisters(result.registers, endian = Endian.Big)
        	decoded.append(decoder.decode_16bit_uint())
                address += i
		print address
	address += 1
	#print address
	print decoded
	modbus.storeFile(datos=decoded,name='carga.txt')
        del decoded[:]
	
	if address == 192:
		print "Se acabo"
		address = 0x00
		print "Empezamos nuevo dia"
		unidad += 1

	"""
        for i in range(0,46):
                address += 1
                result = client.read_holding_registers(address,1,unit=0x01)
                decoder = BinaryPayloadDecoder.fromRegisters(result.registers, endian = Endian.Big)
                decoded.append(decoder.decode_16bit_uint())             

        modbus.storeFile(datos=decoded,name='x.txt')
        del decoded[:]

        for i in range(0,6):
                address += 1
                result = client.read_holding_registers(address,1,unit=0x01)
                decoder = BinaryPayloadDecoder.fromRegisters(result.registers, endian = Endian.Big)
                decoded.append(decoder.decode_16bit_uint())   

        modbus.storeFile2(datos=decoded,name='precio.txt')
        del decoded[:]
	"""

        #return modbus.receive()

def writePayload(dato):
        address = 0x36          #Dirección de memoria del primer registro de escritura

        """
        Se escribiran tantos registros como bytes tenga la trama de datos recibida a traves del puerto serie
        """

        for i in range(0,len(dato)):
                builder = BinaryPayloadBuilder(endian=Endian.Big)

                builder.add_16bit_int(dato[i])

                payload = builder.build()
                client.write_registers(address+i,payload,unit=0x01,skip_encode=True)

        del dato[:]
t0 = time.time()
for i in range(0,2976):
#while 1:
        t2 = time.time()
        
        dato = readPayload()


        inicializacion.init()
        eBrokerInit = setting()
        eBrokerInit.inicia()

        eBrokerProcess = eBroker()
        eBrokerProcess.proceso()

        eBrokerInit.save()

        #if dato:
        #        writePayload(dato)
        t1 = time.time()
        print "Tardo en ejecutar:"
        print t1-t2
	while time.time()-t0 < 0.3:
                pass
        t0=time.time()
