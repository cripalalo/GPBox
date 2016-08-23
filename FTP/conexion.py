#!/usr/bin/env python

import paramiko as FTP

#SERVER = '82.223.79.141'
SERVER = '192.168.1.20'
x=FTP.Transport((SERVER,22))

#x.connect(username = 'root',password = 'GTEgte2016')
x.connect(username = 'gpboxremoto',password = 'gtepotencia')

while 1:
	sftp = FTP.SFTPClient.from_transport(x)

	sftp.put('/home/pi/Desktop/eBroker/datos.txt','/home/datos.txt')


	#obtener fichero

	sftp.get('/home/datos.txt','/home/pi/datos.txt')

	print "conectado"
