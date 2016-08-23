#!/usr/bin/env python

import os
import subprocess

date = os.popen("sshpass -p gtepotencia ssh gpboxremoto@192.168.1.20 date").readline()
hora = os.popen("sshpass -p gtepotencia ssh gpboxremoto@192.168.1.20 date +%H").readline()
minuto = os.popen("sshpass -p gtepotencia ssh gpboxremoto@192.168.1.20 date +%S").readline()

sudodate = subprocess.Popen(["sudo","date","--set",date[11:19].rstrip()])
#os.system('date --set %s' % date)

#sudodate.communicate()

pt = [3,3,3,3,3,3,3,3,2,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2]



#print fecha
print len(date)
print pt[int(hora)]
print minuto
print date
