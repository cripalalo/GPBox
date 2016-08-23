#!/usr/bin/env python

import paramiko as FTP

SERVER = '192.168.1.20'
x=FTP.Transport((SERVER,22))

x.connect(username = 'gpboxremoto',password = 'gtepotencia')

sftp = FTP.SFTPClient.from_transport(x)

# Obtener fichero

sftp.get('/usr/optimizados/lapalma_laborables','/usr/files/Xlapalma.txt')

print "conectado"

