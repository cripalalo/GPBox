#!/usr/bin/env python

class definiciones:
	nBat = 1							# Number of batteries
	nLoad = 1								# Number of loads
	nGen = 0
	nDisp = 3+nBat+nLoad+nGen
	potCont = 36					# Electric Power contracted
	totalIntervalos = 96#288000				# Number of intervals in a day
	maxPotencia = 75 						# Electric Power third path
	tp1 = [59.173468,36.490689,8.367731]
	pt = [1,3,3,3,3,3,3,3,2,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2]
	flagDay = 0
	flagMonth = 0

	# RED TRAMO 1
	preRed1D = 0
	prioRed1O = 5
	prioRed1D = 5

	# RED TRAMO 2
	preRed2D = 0
	prioRed2O = 5
	prioRed2D = 5

	# RED TRAMO 3
	preRed3D = 0
	prioRed3O = 5
	prioRed3D = 5

	prioBatO = 5
	prioBatD = 5

	prioLoad = 5

	fecha = []

class festivos:
	festivo1 = "01/01"
	festivo2 = "06/01"
	festivo3 = "29/02"
	festivo4 = "24/03"
	festivo5 = "25/03"
	festivo6 = "13/04"
	festivo7 = "02/05"
	festivo8 = "26/05"
	festivo9 = "15/08"
	festivo10 = "12/10"
	festivo11 = "01/11"
	festivo12 = "06/12"
	festivo13 = "08/12"
	festivo14 = "26/12"

class fecha:
	hora = []
	minuto = []
	dia = []	
