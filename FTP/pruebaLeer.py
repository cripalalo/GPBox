#!/usr/bin/env python

#import lecturaconfig as cfg
import json

resultado = []
config = {}
execfile("config1.cfg",config)

#print config["path"]+config["name"]

f = open(config['path']+config['name'],"r")
x = json.loads(f.read())

f.close()

for i in range(0,len(x)-1):
	entero = int(x[i])
	decimal = float((x[i]-entero)*10000)

	resultado.append(str.join("",("%04X" % entero)))
	resultado.append(str.join("",("%04X" % int(round(decimal)))))

print resultado
print len(resultado)

f = open(config["patheBroker"]+config["eBrokername"],"w")
json.dump(resultado,f)
f.close()
